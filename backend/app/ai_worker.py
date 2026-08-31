"""
AI Worker - Script independiente que procesa casos con IA.
Se ejecuta como subprocess desde el endpoint process-responsible.
Actualiza directamente la tabla ai_results y el status del processing.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import time
import httpx

def run(processing_id: str, case_ids: list):
    from app.infrastructure.database.connection import db_config
    from app.infrastructure.database.models.case import CaseModel
    from app.infrastructure.database.models.processing import ProcessingModel
    from app.infrastructure.repositories.ai_result_repository import SQLAlchemyAIResultRepository
    from app.infrastructure.repositories.catalogo_tiempos_repository import SQLAlchemyCatalogoTiempoRepository
    from app.infrastructure.ai.ai_service import AIService
    from app.infrastructure.ai.ollama_provider import OllamaProvider
    from app.infrastructure.ai.response_parser import ResponseParser
    from app.infrastructure.ai.models import AIConfig
    import uuid

    pid = uuid.UUID(processing_id)
    local_parser = ResponseParser()
    db = db_config.session_factory()

    try:
        print(f"[WORKER] STARTED: processing_id={pid}, cases={len(case_ids)}", flush=True)

        catalog_repo = SQLAlchemyCatalogoTiempoRepository(db)
        ai_result_repo = SQLAlchemyAIResultRepository(db)
        config = AIConfig()
        provider = OllamaProvider()

        from app.infrastructure.ai.ai_service import AIService
        ai_service = AIService(ai_provider=provider)

        case_uuids = [uuid.UUID(cid) for cid in case_ids]
        cases = db.query(CaseModel).filter(CaseModel.id.in_(case_uuids)).all()

        processable_cases = []
        for case in cases:
            if catalog_repo.find_by_path(case.final_category):
                processable_cases.append(case)

        print(f"[WORKER] Cases to process: {len(processable_cases)}", flush=True)

        processing = db.query(ProcessingModel).filter(ProcessingModel.id == pid).first()
        if not processing:
            print(f"[WORKER] Processing record not found!", flush=True)
            return

        results_count = 0
        rejected = 0

        for idx, case in enumerate(processable_cases):
            try:
                time_range = catalog_repo.get_time_range(case.final_category)
                estimated_minutes = (time_range["min"] + time_range["max"]) // 2

                case_data = {
                    "case_code": case.case_code,
                    "case_type": case.case_type,
                    "final_category": case.final_category,
                    "description": case.description,
                    "solution": case.solution or "",
                }

                prompt = ai_service._build_description_context(case_data)

                start_time = time.time()
                print(f"[WORKER] {idx+1}/{len(processable_cases)}: {case.case_code} ({case.case_type})", flush=True)

                with httpx.Client(timeout=config.timeout) as client:
                    response = client.post(
                        f"{provider.base_url}/api/generate",
                        json={
                            "model": config.model,
                            "prompt": prompt,
                            "stream": False,
                            "options": {
                                "temperature": config.temperature,
                                "num_predict": config.max_tokens,
                            },
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    latency_ms = (time.time() - start_time) * 1000
                    ai_content = data.get("response", "")
                    tokens_used = data.get("eval_count", 0)

                if ai_content:
                    parsed = local_parser.parse_description(ai_content)
                    generated_description = parsed.text

                    ai_result_repo.save(
                        processing_id=pid,
                        case_id=case.id,
                        case_code=case.case_code,
                        estimated_minutes=estimated_minutes,
                        generated_description=generated_description,
                        model_name=config.model,
                        tokens_used=tokens_used,
                        latency_ms=latency_ms,
                    )
                    results_count += 1
                    print(f"[WORKER] OK: '{generated_description[:60]}...' ({latency_ms:.0f}ms)", flush=True)
                else:
                    rejected += 1
                    print(f"[WORKER] REJECTED (empty AI response)", flush=True)

            except Exception as e:
                rejected += 1
                print(f"[WORKER] ERROR: {e}", flush=True)

        processing.status = "completed"
        processing.processed_cases = results_count
        processing.rejected_cases = rejected
        db.commit()

        print(f"[WORKER] COMPLETED: processed={results_count}, rejected={rejected}", flush=True)

    except Exception as e:
        print(f"[WORKER] FATAL: {e}", flush=True)
        import traceback
        traceback.print_exc()
        try:
            processing = db.query(ProcessingModel).filter(ProcessingModel.id == pid).first()
            if processing:
                processing.status = "failed"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


if __name__ == "__main__":
    print(f"[WORKER] sys.argv: {sys.argv}", flush=True)
    proc_id = sys.argv[1]
    ids_str = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else ""
    ids = ids_str.split(",") if ids_str else []
    print(f"[WORKER] proc_id={proc_id}, ids_count={len(ids)}", flush=True)
    run(proc_id, ids)
