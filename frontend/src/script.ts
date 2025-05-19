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

// Function to fetch all articles from backend
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

// // Function to fetch replies for a specific comment
// export async function fetchReplies(parentID: string) {
//   try {
//     const res = await fetch(`/api/replies/${parentID}`, {
//       credentials: 'include', // Include cookies in the request for session data
//     });
//     if (!res.ok) {
//       throw new Error(`Failed to fetch comments: ${res.status}`);
//     }
//     return await res.json();
//   } catch (error) {
//     console.error("Error fetching comments:", error);
//     return [];
//   }
// }

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

// Function to submit a new comment
export async function replyComment(articleID: string, parentID: string, commentText: string) {
  if (commentText.trim() === '') {
    return false;
  }
  try {
    const response = await fetch('/api/reply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include', // Include cookies in the request for session data
      body: JSON.stringify({
        articleID: articleID,
        parentID: parentID,
        text: commentText
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to submit reply: ${response.status}`);
    }

    return true;
  } catch (error) {
    console.error("Error submitting reply:", error);
    return false;
  }
}

// Function for mod/admin to mark comment as deleted
export async function moderateComment(commentId: string) {
  try {
    const response = await fetch(`api/moderate/${commentId}`, {
      method: "PUT",
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        replace: "Comment deleted by mod"
      })
    });
    if (!response.ok) {
      throw new Error(`Failed to delete comment: ${response.status}`);
    }
    return true
  } catch (error) {
    console.error("Error deleting comment:", error);
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