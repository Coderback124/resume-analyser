import { useState } from "react";
import {
  uploadFile,
  improveResume,
  downloadResumePdf,
} from "../services/api";


function FileUpload() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);

  const [improvedResume, setImprovedResume] = useState("");
  const [generatedResume, setGeneratedResume] = useState("");

  const [loading, setLoading] = useState(false);
  const [improving, setImproving] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [copied, setCopied] = useState(false);


  // =========================================================
  // ANALYSE RESUME
  // =========================================================

  const handleUpload = async () => {
    if (!file) {
      alert("Please upload a CV");
      return;
    }

    try {
      setLoading(true);

      // Clear previous results before a new analysis.
      setResult(null);
      setImprovedResume("");
      setGeneratedResume("");
      setCopied(false);

      const data = await uploadFile(
        file,
        jobDescription
      );

      setResult(data);

      setTimeout(() => {
        document
          .getElementById("analysis-results")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 200);

    } catch (error) {
      alert(
        error.message ||
        "Resume analysis failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };


  // =========================================================
  // IMPROVE RESUME WITH AI
  // =========================================================

  const handleImproveResume = async () => {
    if (!result?.original_resume) {
      alert(
        "The original resume text is not available. Please analyse the resume again."
      );
      return;
    }

    try {
      setImproving(true);
      setCopied(false);

      const data = await improveResume(
        result.original_resume,
        jobDescription,
        result.feedback || []
      );

      const newResume = data.improved_resume || "";

      if (!newResume.trim()) {
        throw new Error(
          "The improved resume was empty"
        );
      }

      setImprovedResume(newResume);
      setGeneratedResume(newResume);

      setTimeout(() => {
        document
          .getElementById("improved-resume")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 200);

    } catch (error) {
      alert(
        error.message ||
        "Could not improve the resume. Please try again."
      );
    } finally {
      setImproving(false);
    }
  };


  // =========================================================
  // COPY IMPROVED RESUME
  // =========================================================

  const handleCopy = async () => {
    if (!improvedResume.trim()) {
      return;
    }

    try {
      await navigator.clipboard.writeText(
        improvedResume
      );

      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 2000);

    } catch {
      alert(
        "Could not copy the resume to the clipboard."
      );
    }
  };


  // =========================================================
  // UNDO MANUAL EDITS
  // =========================================================

  const handleUndoChanges = () => {
    if (!generatedResume) {
      return;
    }

    setImprovedResume(generatedResume);
    setCopied(false);
  };


  // =========================================================
  // DOWNLOAD PDF
  // =========================================================

  const handleDownloadPdf = async () => {
    if (!improvedResume.trim()) {
      alert(
        "There is no improved resume to download."
      );
      return;
    }

    try {
      setDownloading(true);

      const blob = await downloadResumePdf(
        improvedResume,
        "improved_resume.pdf"
      );

      const downloadUrl =
        window.URL.createObjectURL(blob);

      const link =
        document.createElement("a");

      link.href = downloadUrl;
      link.download = "improved_resume.pdf";

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(
        downloadUrl
      );

    } catch (error) {
      alert(
        error.message ||
        "Could not download the PDF. Please try again."
      );
    } finally {
      setDownloading(false);
    }
  };


  // =========================================================
  // FILE HANDLING
  // =========================================================

  const handleDrop = (event) => {
    event.preventDefault();

    const droppedFile =
      event.dataTransfer.files?.[0];

    if (droppedFile) {
      setFile(droppedFile);
    }
  };


  // =========================================================
  // SCORE HELPERS
  // =========================================================

  const getScoreColor = (score) => {
    const numericScore = Number(score) || 0;

    if (numericScore >= 80) {
      return "#16a34a";
    }

    if (numericScore >= 60) {
      return "#f59e0b";
    }

    return "#ef4444";
  };


  const resumeScore = result
    ? Math.round(
        (
          Number(result.score) /
          Number(result.max_score || 100)
        ) * 100
      )
    : 0;


  // =========================================================
  // UI
  // =========================================================

  return (
    <div>

      {/* =====================================================
          UPLOAD BOX
      ====================================================== */}

      <div
        onDrop={handleDrop}
        onDragOver={(event) =>
          event.preventDefault()
        }
        style={{
          border: "2px dashed #d1d5db",
          padding: "25px",
          borderRadius: "10px",
          textAlign: "center",
          marginBottom: "15px",
          background: "#fafafa",
        }}
      >
        {file ? (
          <p>
            <strong>{file.name}</strong>
          </p>
        ) : (
          <p
            style={{
              color: "#6b7280",
            }}
          >
            Drag & drop your CV here
          </p>
        )}
      </div>


      {/* =====================================================
          FILE INPUT
      ====================================================== */}

      <input
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={(event) => {
          const selectedFile =
            event.target.files?.[0];

          if (selectedFile) {
            setFile(selectedFile);
          }
        }}
      />


      {/* =====================================================
          JOB DESCRIPTION
      ====================================================== */}

      <textarea
        placeholder="Paste job description here..."
        value={jobDescription}
        onChange={(event) =>
          setJobDescription(
            event.target.value
          )
        }
        style={{
          width: "100%",
          boxSizing: "border-box",
          marginTop: "15px",
          padding: "12px",
          height: "120px",
          borderRadius: "8px",
          border: "1px solid #d1d5db",
          resize: "vertical",
        }}
      />


      {/* =====================================================
          ANALYSE BUTTON
      ====================================================== */}

      <button
        onClick={handleUpload}
        disabled={loading}
        style={{
          marginTop: "15px",
          width: "100%",
          padding: "14px",
          background: loading
            ? "#a5b4fc"
            : "#4f46e5",
          color: "white",
          border: "none",
          borderRadius: "8px",
          fontWeight: "600",
          cursor: loading
            ? "not-allowed"
            : "pointer",
        }}
      >
        {loading
          ? "Analyzing resume..."
          : "Analyse Resume"}
      </button>


      {/* =====================================================
          RESULTS
      ====================================================== */}

      {result && (
        <div
          id="analysis-results"
          style={{
            marginTop: "30px",
            scrollMarginTop: "30px",
          }}
        >

          {/* =================================================
              SCORE CARDS
          ================================================== */}

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(3, minmax(0, 1fr))",
              gap: "15px",
              marginBottom: "25px",
            }}
          >

            {/* Resume Strength */}

            <div
              style={{
                background: "#ffffff",
                padding: "20px",
                borderRadius: "10px",
                boxShadow:
                  "0 4px 15px rgba(0,0,0,0.05)",
                textAlign: "center",
              }}
            >
              <h4
                style={{
                  color: "#6b7280",
                }}
              >
                Resume Strength
              </h4>

              <h2
                style={{
                  color:
                    getScoreColor(
                      resumeScore
                    ),
                  marginTop: "8px",
                }}
              >
                {resumeScore}%
              </h2>
            </div>


            {/* ATS Compatibility */}

            <div
              style={{
                background: "#ffffff",
                padding: "20px",
                borderRadius: "10px",
                boxShadow:
                  "0 4px 15px rgba(0,0,0,0.05)",
                textAlign: "center",
              }}
            >
              <h4
                style={{
                  color: "#6b7280",
                }}
              >
                ATS Compatibility
              </h4>

              <h2
                style={{
                  color:
                    getScoreColor(
                      result.ats_score
                    ),
                  marginTop: "8px",
                }}
              >
                {result.ats_score ?? 0}%
              </h2>
            </div>


            {/* Job Fit */}

            <div
              style={{
                background: "#ffffff",
                padding: "20px",
                borderRadius: "10px",
                boxShadow:
                  "0 4px 15px rgba(0,0,0,0.05)",
                textAlign: "center",
              }}
            >
              <h4
                style={{
                  color: "#6b7280",
                }}
              >
                Job Fit
              </h4>

              <h2
                style={{
                  color:
                    getScoreColor(
                      result.job_match_score
                    ),
                  marginTop: "8px",
                }}
              >
                {result.job_match_score ?? 0}%
              </h2>
            </div>

          </div>


          {/* =================================================
              FEEDBACK
          ================================================== */}

          <div
            style={{
              background: "#ffffff",
              padding: "20px",
              borderRadius: "10px",
              boxShadow:
                "0 4px 15px rgba(0,0,0,0.05)",
            }}
          >
            <h3
              style={{
                marginBottom: "15px",
              }}
            >
              Feedback
            </h3>

            {!result.feedback ||
            result.feedback.length === 0 ? (
              <p
                style={{
                  color: "#16a34a",
                }}
              >
                Strong CV — no major issues found
              </p>
            ) : (
              result.feedback.map(
                (item, index) => (
                  <div
                    key={`${item}-${index}`}
                    style={{
                      padding: "10px",
                      borderBottom:
                        index ===
                        result.feedback.length - 1
                          ? "none"
                          : "1px solid #eee",
                    }}
                  >
                    {item}
                  </div>
                )
              )
            )}


            {/* =============================================
                IMPROVE BUTTON
            ============================================== */}

            <button
              onClick={handleImproveResume}
              disabled={improving}
              style={{
                marginTop: "20px",
                width: "100%",
                padding: "14px",
                background: improving
                  ? "#a5b4fc"
                  : "#4f46e5",
                color: "white",
                border: "none",
                borderRadius: "8px",
                fontWeight: "600",
                cursor: improving
                  ? "not-allowed"
                  : "pointer",
              }}
            >
              {improving
                ? "Improving your resume..."
                : "Improve My Resume"}
            </button>

          </div>

        </div>
      )}


      {/* =====================================================
          IMPROVED RESUME EDITOR
      ====================================================== */}

      {improvedResume && (
        <div
          id="improved-resume"
          style={{
            marginTop: "30px",
            padding: "20px",
            background: "#ffffff",
            borderRadius: "10px",
            boxShadow:
              "0 4px 15px rgba(0,0,0,0.05)",
            scrollMarginTop: "30px",
          }}
        >
          <div
            style={{
              marginBottom: "15px",
            }}
          >
            <h3
              style={{
                marginBottom: "6px",
              }}
            >
              Your Improved Resume
            </h3>

            <p
              style={{
                margin: 0,
                color: "#6b7280",
                fontSize: "14px",
              }}
            >
              Review and edit the text before
              downloading your PDF.
            </p>
          </div>


          {/* EDITABLE TEXT AREA */}

          <textarea
            value={improvedResume}
            onChange={(event) => {
              setImprovedResume(
                event.target.value
              );

              setCopied(false);
            }}
            style={{
              width: "100%",
              boxSizing: "border-box",
              minHeight: "600px",
              padding: "18px",
              border:
                "1px solid #d1d5db",
              borderRadius: "8px",
              resize: "vertical",
              fontFamily:
                "Arial, sans-serif",
              fontSize: "14px",
              lineHeight: "1.6",
              background: "#fafafa",
            }}
          />


          {/* ACTION BUTTONS */}

          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "10px",
              marginTop: "15px",
            }}
          >

            <button
              onClick={handleCopy}
              style={{
                flex: "1 1 150px",
                padding: "12px",
                background: "#ffffff",
                color: "#374151",
                border:
                  "1px solid #d1d5db",
                borderRadius: "8px",
                fontWeight: "600",
                cursor: "pointer",
              }}
            >
              {copied
                ? "Copied!"
                : "Copy Resume"}
            </button>


            <button
              onClick={handleUndoChanges}
              disabled={
                improvedResume ===
                generatedResume
              }
              style={{
                flex: "1 1 150px",
                padding: "12px",
                background: "#ffffff",
                color: "#374151",
                border:
                  "1px solid #d1d5db",
                borderRadius: "8px",
                fontWeight: "600",
                cursor:
                  improvedResume ===
                  generatedResume
                    ? "not-allowed"
                    : "pointer",
                opacity:
                  improvedResume ===
                  generatedResume
                    ? 0.5
                    : 1,
              }}
            >
              Undo My Edits
            </button>


            <button
              onClick={handleDownloadPdf}
              disabled={downloading}
              style={{
                flex: "1 1 180px",
                padding: "12px",
                background: downloading
                  ? "#a5b4fc"
                  : "#4f46e5",
                color: "white",
                border: "none",
                borderRadius: "8px",
                fontWeight: "600",
                cursor: downloading
                  ? "not-allowed"
                  : "pointer",
              }}
            >
              {downloading
                ? "Creating PDF..."
                : "Download PDF"}
            </button>

          </div>
        </div>
      )}

    </div>
  );
}


export default FileUpload;