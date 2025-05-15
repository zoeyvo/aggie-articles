
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
    const articlesRes = await fetch("/api/articles");
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