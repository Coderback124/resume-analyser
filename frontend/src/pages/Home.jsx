import FileUpload from "../components/FileUpload";

function Home() {
  return (
    <div style={{
      minHeight: "100vh",
      background: "#f5f7fb",
      padding: "40px 20px"
    }}>
      
      {/* Header */}
      <div style={{
        textAlign: "center",
        marginBottom: "30px"
      }}>
        <h1 style={{ fontSize: "32px" }}>
          AI Resume Analyzer
        </h1>
        <p style={{ color: "#6b7280" }}>
          Improve your resume and match it to jobs instantly
        </p>
      </div>

      {/* Main Card */}
      <div style={{
        maxWidth: "600px",
        margin: "0 auto",
        background: "#ffffff",
        padding: "30px",
        borderRadius: "12px",
        boxShadow: "0 10px 30px rgba(0,0,0,0.08)"
      }}>
        <FileUpload />
      </div>

    </div>
  );
}

export default Home;