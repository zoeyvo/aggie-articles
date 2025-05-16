// Formatting for current datem, e.g. "Weekday, Month Day, Year"
export function getDate() {
  const date = new Date();
  const options: Intl.DateTimeFormatOptions = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  return date.toLocaleDateString("en-US", options);
}


export async function getArticles() {
  let articles: any[] = []; // Array to store fetched articles

  try {
    const articlesRes = await fetch("/api/articles", {
      credentials: 'include', // Include cookies in the request for session data
    });
    if (!articlesRes.ok) {
      throw new Error(`HTTP error! status: ${articlesRes.status}`);
    }
    const articlesData = await articlesRes.json();
    articles = articlesData.response?.docs || [];
    console.log("Fetched articles:", JSON.stringify(articles, null, 2));
  } catch (error) {
    console.error("Failed to fetch data:", error);
  }

  return articles;
}

// Function to fetch comments for a specific article
export async function fetchComments(articleID: string) {
  try {
    const res = await fetch(`/api/comments/${articleID}`, {
      credentials: 'include', // Include cookies in the request for session data
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch comments: ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error("Error fetching comments:", error);
    return [];
  }
}

// Function to submit a new comment
export async function submitComment(articleID: string, commentText: string) {
  if (commentText.trim() === '') {
    return false;
  }
    try {
    const response = await fetch('/api/comments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include', // Include cookies in the request for session data
      body: JSON.stringify({
        articleID: articleID,
        text: commentText
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to submit comment: ${response.status}`);
    }
    
    return true;
  } catch (error) {
    console.error("Error submitting comment:", error);
    return false;
  }
}

// Function to get the current authenticated user (if any)
export async function getAuthenticatedUser() {
  try {
    console.log('Fetching authentication status...');
    
    // Add random query parameter to prevent caching
    const cacheBuster = new Date().getTime();
    
    const response = await fetch(`/api/user?t=${cacheBuster}`, {
      credentials: 'include', // Include cookies in the request for session data
      headers: {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache', // Prevent caching of authentication status
        'Pragma': 'no-cache'
      }
    });
    
    if (response.ok) {
      const userData = await response.json();
      console.log('Authentication response:', userData);
      return userData;
    } else {
      console.warn('Failed to fetch authentication status:', response.status);
      return { authenticated: false };
    }
  } catch (error) {
    console.error('Error fetching user info:', error);
    return { authenticated: false };
  }
}