const API_URL = import.meta.env.VITE_API_URL;


const getErrorMessage = async (response, fallbackMessage) => {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    return fallbackMessage;
  } catch {
    return fallbackMessage;
  }
};


export const uploadFile = async (file, jobDescription) => {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("job_description", jobDescription);

  const response = await fetch(`${API_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const message = await getErrorMessage(
      response,
      "Resume analysis failed"
    );

    throw new Error(message);
  }

  return response.json();
};


export const improveResume = async (
  originalResume,
  jobDescription,
  feedback
) => {
  const response = await fetch(`${API_URL}/improve-resume`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      original_resume: originalResume,
      job_description: jobDescription,
      feedback,
    }),
  });

  if (!response.ok) {
    const message = await getErrorMessage(
      response,
      "Could not improve the resume"
    );

    throw new Error(message);
  }

  return response.json();
};


export const downloadResumePdf = async (
  resumeText,
  filename = "improved_resume.pdf"
) => {
  const response = await fetch(`${API_URL}/resume-pdf`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      resume_text: resumeText,
      filename,
    }),
  });

  if (!response.ok) {
    const message = await getErrorMessage(
      response,
      "Could not create the PDF"
    );

    throw new Error(message);
  }

  return response.blob();
};