import React from "react";
import { useState } from "react";
import UploadPage from "./pages/UploadPage.jsx";
import ResponsiblePage from "./pages/ResponsiblePage.jsx";
import ResultsPage from "./pages/ResultsPage.jsx";

function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [report, setReport] = useState(null);

  if (report) {
    return (
      <ResultsPage
        report={report}
        onBack={() => setReport(null)}
        onStartOver={() => {
          setReport(null);
          setUploadedFile(null);
        }}
      />
    );
  }

  if (uploadedFile) {
    return (
      <ResponsiblePage
        file={uploadedFile}
        onBack={() => setUploadedFile(null)}
        onGenerate={setReport}
      />
    );
  }

  return <UploadPage onFileSelected={setUploadedFile} />;
}

export default App;