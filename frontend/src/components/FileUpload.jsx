import { useState } from "react";
import { uploadFile } from "../services/api";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please upload a CV");
      return;
    }

    try {
      setLoading(true);

      const data = await uploadFile(file, jobDescription);
      setResult(data);

      // ✅ Smooth scroll to results
      setTimeout(() => {
        window.scrollTo({
          top: document.body.scrollHeight,
          behavior: "smooth"
        });
      }, 200);

    } catch (err) {
      alert("Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setFile(e.dataTransfer.files[0]);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "#16a34a";
    if (score >= 60) return "#f59e0b";
    return "#ef4444";
  };

  const resumeScore = result
    ? Math.round(
        (Number(result.score) / Number(result.max_score || 6)) * 100
      )
    : 0;

  return (
    <div>

      {/* Upload Box */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
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
          <p><strong>{file.name}</strong></p>
        ) : (
          <p style={{ color: "#6b7280" }}>
            Drag & drop your CV here
          </p>
        )}
      </div>

      {/* File Input */}
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      {/* Job Description */}
      <textarea
        placeholder="Paste job description here..."
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
        style={{
          width: "100%",
          marginTop: "15px",
          padding: "12px",
          height: "120px",
          borderRadius: "8px",
          border: "1px solid #d1d5db",
        }}
      />

      {/* Button (LOADING FIXED) */}
      <button
        onClick={handleUpload}
        disabled={loading}
        style={{
          marginTop: "15px",
          width: "100%",
          padding: "14px",
          background: loading ? "#a5b4fc" : "#4f46e5",
          color: "white",
          border: "none",
          borderRadius: "8px",
          fontWeight: "600",
          cursor: loading ? "not-allowed" : "pointer"
        }}
      >
        {loading ? "Analyzing resume..." : "Analyse Resume"}
      </button>

      {/* RESULTS */}
      {result && (
        <div style={{ marginTop: "30px" }}>

          {/* SCORE CARDS */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: "15px",
            marginBottom: "25px"
          }}>

            {/* Resume Score */}
            <div style={{
              background: "#ffffff",
              padding: "20px",
              borderRadius: "10px",
              boxShadow: "0 4px 15px rgba(0,0,0,0.05)",
              textAlign: "center"
            }}>
              <h4 style={{ color: "#6b7280" }}>Resume Strength</h4>
              <h2 style={{
                color: getScoreColor(resumeScore),
                marginTop: "8px"
              }}>
                {resumeScore}%
              </h2>
            </div>

            {/* ATS Score */}
            <div style={{
              background: "#ffffff",
              padding: "20px",
              borderRadius: "10px",
              boxShadow: "0 4px 15px rgba(0,0,0,0.05)",
              textAlign: "center"
            }}>
              <h4 style={{ color: "#6b7280" }}>ATS Compatibility</h4>
              <h2 style={{
                color: getScoreColor(result.ats_score || 0),
                marginTop: "8px"
              }}>
                {result.ats_score ?? 0}%
              </h2>
            </div>

            {/* Job Match */}
            <div style={{
              background: "#ffffff",
              padding: "20px",
              borderRadius: "10px",
              boxShadow: "0 4px 15px rgba(0,0,0,0.05)",
              textAlign: "center"
            }}>
              <h4 style={{ color: "#6b7280" }}>Job Fit</h4>
              <h2 style={{
                color: getScoreColor(result.job_match_score || 0),
                marginTop: "8px"
              }}>
                {result.job_match_score ?? 0}%
              </h2>
            </div>

          </div>

          {/* FEEDBACK */}
          <div style={{
            background: "#ffffff",
            padding: "20px",
            borderRadius: "10px",
            boxShadow: "0 4px 15px rgba(0,0,0,0.05)"
          }}>
            <h3 style={{ marginBottom: "15px" }}>
              Feedback
            </h3>

            {result.feedback.length === 0 ? (
              <p style={{ color: "#16a34a" }}>
                Strong CV — no major issues found
              </p>
            ) : (
              result.feedback.map((item, index) => (
                <div key={index} style={{
                  padding: "10px",
                  borderBottom: "1px solid #eee"
                }}>
                  {item}
                </div>
              ))
            )}
          </div>

        </div>
      )}
    </div>
  );
}

export default FileUpload;