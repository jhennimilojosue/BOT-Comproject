import React, { useCallback, useEffect, useMemo, useState } from "react";
import { processResponsible, getResults } from "../api.js";
import "./ResultsPage.css";

const formatDate = (date) => new Intl.DateTimeFormat("es-CO", {
  day: "2-digit",
  month: "short",
  year: "numeric",
}).format(new Date(`${date}T12:00:00`));

const formatMinutes = (minutes) => {
  const hours = Number(minutes) / 60;
  if (Number.isNaN(hours)) return "";
  return `${hours.toLocaleString("es-CO", { maximumFractionDigits: 2 })} h`;
};

const formatWeekOption = (week) =>
  `${formatDate(week.fecha_inicio)} – ${formatDate(week.fecha_fin)}`;

function ResultsPage({ report, onBack, onStartOver }) {
  const uploadId = report?.file?.uploadId;
  const processingId = report?.file?.processingId;
  const responsible = report?.responsible;
  const fileName = report?.file?.file?.name || report?.file?.name || "";

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);
  const [activeProcessingId, setActiveProcessingId] = useState(processingId);

  const [filters, setFilters] = useState({
    caseNumber: "",
    client: "",
    project: "",
  });
  const [week, setWeek] = useState("");
  const [editedSummaries, setEditedSummaries] = useState({});
  const [editingCaseId, setEditingCaseId] = useState(null);
  const [draftSummary, setDraftSummary] = useState("");

  const weekKey = (weekItem) =>
    weekItem ? `${weekItem.fecha_inicio}|${weekItem.fecha_fin}` : "";

  const loadResults = useCallback(async (processingIdToUse, semana) => {
    try {
      const payload = await getResults(processingIdToUse, semana?.fecha_inicio, semana?.fecha_fin);
      setData(payload);
      setWeek(weekKey(semana));
    } catch (err) {
      setError(err.message || "No se pudieron obtener los resultados.");
    }
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");

    const run = async () => {
      try {
        const processed = await processResponsible(uploadId, responsible);
        if (!active) return;
        setActiveProcessingId(processed.processing_id || processingId);
        await loadResults(processed.processing_id || processingId, null);
      } catch (err) {
        if (!active) return;
        const fallback = async () => {
          try {
            const payload = await getResults(processingId);
            setData(payload);
          } catch (fallbackErr) {
            setError(err.message || fallbackErr.message || "No se pudo procesar el responsable.");
          }
        };
        await fallback();
      } finally {
        if (active) setLoading(false);
      }
    };

    run();
    return () => {
      active = false;
    };
  }, [uploadId, responsible, processingId, loadResults]);

  const handleWeekChange = async (event) => {
    const weekKeyValue = event.target.value;
    setWeek(weekKeyValue);
    const semana = (data?.semanas_disponibles || []).find(
      (w) => `${w.fecha_inicio}|${w.fecha_fin}` === weekKeyValue
    );
    await loadResults(activeProcessingId, semana || null);
    setTimeout(() => document.getElementById("cases-title")?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
  };

  const results = data?.results || [];
  const clients = [...new Set(results.map((item) => item.cliente).filter(Boolean))];
  const projects = [...new Set(results.map((item) => item.area).filter(Boolean))];

  const visibleCases = useMemo(() => results.filter((item) => {
    const caseNumber = filters.caseNumber.trim().toLowerCase();
    return (!caseNumber || item.case_code.toLowerCase().includes(caseNumber))
      && (!filters.client || item.cliente === filters.client)
      && (!filters.project || item.area === filters.project);
  }), [results, filters]);

  const updateFilter = (name, value) => setFilters((current) => ({ ...current, [name]: value }));
  const clearFilters = async () => {
    setFilters({ caseNumber: "", client: "", project: "" });
    if (week) {
      await loadResults(activeProcessingId, null);
    }
  };
  const startEditing = (item) => {
    setEditingCaseId(item.case_code);
    setDraftSummary(editedSummaries[item.case_code] ?? item.generated_description);
  };
  const saveSummary = (caseCode) => {
    setEditedSummaries((current) => ({ ...current, [caseCode]: draftSummary.trim() }));
    setEditingCaseId(null);
    setDraftSummary("");
  };
  const cancelEditing = () => {
    setEditingCaseId(null);
    setDraftSummary("");
  };

  return (
    <main className="upload-page results-page">
      <div className="upload-page__glow upload-page__glow--top" aria-hidden="true" />
      <div className="upload-page__glow upload-page__glow--bottom" aria-hidden="true" />

      <section className="results-content" aria-labelledby="results-title">
        <div className="results-topbar">
          <button className="results-back" type="button" onClick={onBack}>
            <svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m12.5 4.5-5.5 5.5 5.5 5.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
            Volver a selección
          </button>
          <button className="results-restart" type="button" onClick={onStartOver}>Cargar otro archivo</button>
        </div>

        <div className="results-heading">
          <div className="results-brand-mark" aria-hidden="true">
            <svg viewBox="0 0 40 40" fill="none">
              <path d="M11 12.5h18M11 20h12M11 27.5h8" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
              <path d="m25 24 3.5 3.5L35 20" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <p className="upload-eyebrow">PASO 3 DE 3 · REPORTE</p>
          <h1 className="project-title" id="results-title">Bot-ComProject</h1>
          <p className="results-subtitle">
            {loading ? "Procesando los casos con IA…" : "Casos preparados para revisar y filtrar."}
          </p>
        </div>

        <div className="results-summary">
          <div className="results-summary__person">
            <span className="results-avatar" aria-hidden="true">{responsible?.split(" ").slice(0, 2).map((part) => part[0]).join("")}</span>
            <div>
              <span className="results-summary__label">Responsable</span>
              <strong>{responsible}</strong>
            </div>
          </div>
          <span className="results-summary__separator" aria-hidden="true" />
          <div className="results-summary__detail">
            <span className="results-summary__label">Grupo</span>
            <strong>{report.group}</strong>
          </div>
          <span className="results-summary__separator" aria-hidden="true" />
          <div className="results-summary__detail results-summary__file">
            <span className="results-summary__label">Archivo</span>
            <strong title={fileName}>{fileName}</strong>
          </div>
        </div>

        {error && (
          <p className="responsible-error" role="alert">{error}</p>
        )}

        {loading ? (
          <section className="processing-card" aria-live="polite">
            <span className="processing-card__spinner" aria-hidden="true">
              <svg viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="18" stroke="currentColor" strokeWidth="3.2" strokeOpacity="0.3" />
                <path d="M42 24a18 18 0 0 0-18-18" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" />
              </svg>
            </span>
            <h2>Generando reporte con IA</h2>
            <p>Se están analizando los casos de {responsible} contra el catálogo de tiempos. Esto puede tardar unos minutos.</p>
          </section>
        ) : data ? (
          <>
            <section className="results-stats" aria-label="Resumen del procesamiento">
              <div className="results-stats__item">
                <span className="results-stats__label">Casos procesados</span>
                <strong>{data.total_results_all}</strong>
              </div>
              <div className="results-stats__item">
                <span className="results-stats__label">Horas estimadas</span>
                <strong>{formatMinutes(data.summary?.total_hours)}</strong>
              </div>
              <div className="results-stats__item">
                <span className="results-stats__label">Tiempo promedio</span>
                <strong>{data.summary?.avg_minutes ? formatMinutes(data.summary.avg_minutes) : "—"}</strong>
              </div>
            </section>

            <section className="filters-card" aria-label="Filtros del reporte">
              <div className="filters-card__heading">
                <div>
                  <h2>Filtros</h2>
                  <p>Afina los casos que quieres consultar.</p>
                </div>
                <button className="clear-filters" type="button" onClick={clearFilters}>Limpiar filtros</button>
              </div>
              <div className="filters-grid">
                <label className="filter-field filter-field--case-number">
                  <span>Número de caso</span>
                  <span className="search-input-wrap">
                    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="8.8" cy="8.8" r="5.8" stroke="currentColor" strokeWidth="1.5" /><path d="m13.2 13.2 4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /></svg>
                    <input inputMode="numeric" type="search" value={filters.caseNumber} placeholder="Buscar número de caso" onChange={(event) => updateFilter("caseNumber", event.target.value)} />
                  </span>
                </label>
                <label className="filter-field">
                  <span>Semana</span>
                  <select value={week} onChange={handleWeekChange}>
                    <option value="">Todas las semanas</option>
                    {(data.semanas_disponibles || []).map((w) => (
                      <option key={`${w.fecha_inicio}|${w.fecha_fin}`} value={`${w.fecha_inicio}|${w.fecha_fin}`}>
                        {formatWeekOption(w)} · {w.count} casos
                      </option>
                    ))}
                  </select>
                </label>
                <label className="filter-field">
                  <span>Cliente</span>
                  <select value={filters.client} onChange={(event) => updateFilter("client", event.target.value)}>
                    <option value="">Todos los clientes</option>
                    {clients.map((client) => <option key={client} value={client}>{client}</option>)}
                  </select>
                </label>
                <label className="filter-field">
                  <span>Área</span>
                  <select value={filters.project} onChange={(event) => updateFilter("project", event.target.value)}>
                    <option value="">Todas las áreas</option>
                    {projects.map((project) => <option key={project} value={project}>{project}</option>)}
                  </select>
                </label>
              </div>
            </section>

            <section className="cases-section" aria-labelledby="cases-title">
              <div className="cases-heading">
                <div>
                  <h2 id="cases-title">Detalle de casos</h2>
                  <p><strong>{visibleCases.length}</strong> {visibleCases.length === 1 ? "caso encontrado" : "casos encontrados"}</p>
                </div>
              </div>

              <div className="cases-table-wrap" role="region" aria-label="Tabla de casos; desplázate horizontalmente para ver todas las columnas" tabIndex="0">
                <table className="cases-table">
                  <thead>
                    <tr>
                      <th scope="col">Caso</th>
                      <th scope="col">Cliente</th>
                      <th scope="col">Tipo</th>
                      <th scope="col">Área</th>
                      <th scope="col">Fecha de solución</th>
                      <th scope="col">Descripción generada</th>
                      <th scope="col">Tiempo</th>
                      <th scope="col">Acción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visibleCases.map((item) => (
                      <tr key={item.case_code}>
                        <td><span className="case-id">{item.case_code}</span></td>
                        <td>{item.cliente || "—"}</td>
                        <td><span className={`case-type-tag case-type-tag--${(item.case_type || "").toLowerCase()}`}>{item.case_type}</span></td>
                        <td>{item.area || "—"}</td>
                        <td className="case-date">{item.fecha_solucion ? formatDate(item.fecha_solucion) : "—"}</td>
                        <td className="case-long-text case-generated">
                          {editingCaseId === item.case_code ? (
                            <div className="summary-editor">
                              <textarea
                                aria-label={`Editar descripción generada del caso ${item.case_code}`}
                                value={draftSummary}
                                rows={4}
                                onChange={(event) => setDraftSummary(event.target.value)}
                              />
                              <div className="summary-editor__actions">
                                <button type="button" className="summary-save" disabled={!draftSummary.trim()} onClick={() => saveSummary(item.case_code)}>Guardar</button>
                                <button type="button" className="summary-cancel" onClick={cancelEditing}>Cancelar</button>
                              </div>
                            </div>
                          ) : (editedSummaries[item.case_code] ?? item.generated_description)}
                        </td>
                        <td className="case-time">{formatMinutes(item.estimated_minutes)}</td>
                        <td>
                          {editingCaseId !== item.case_code && (
                            <button className="edit-summary-button" type="button" onClick={() => startEditing(item)} aria-label={`Editar descripción del caso ${item.case_code}`}>
                              <svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m12.7 4.3 3 3M4 16l3.2-.7L16 6.5a1.8 1.8 0 0 0-2.5-2.5l-8.8 8.8L4 16Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
                              Editar
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                    {visibleCases.length === 0 && (
                      <tr><td className="empty-results" colSpan="8">No hay casos que coincidan con estos filtros.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
              <p className="results-disclaimer">Los datos provienen de los resultados generados por IA para este reporte. Las categorías, tiempos y descripciones se obtienen del catálogo y los casos del archivo.</p>
            </section>
          </>
        ) : (
          <p className="responsible-empty">Aún no hay resultados para mostrar.</p>
        )}
      </section>
    </main>
  );
}

export default ResultsPage;