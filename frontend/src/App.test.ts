import { expect, test, afterEach } from "vitest";
import { cleanup, getByRole, render } from "@testing-library/svelte";
import App from "./App.svelte";
import "./script";
import { getArticles, getDate } from "./script";

// Clear the rendered app after each test
afterEach(() => {
  cleanup();
})

test('Overall Render', async () => {
  render(App);
});

test("Test if Article compenent displays content correctly", async () => {
  const articles = [
    {
      multimedia: {
        default: { url: "test_img.png" },
        caption: "This is img caption"
      },
      headline: { main: "Title" },
      snippet: "This is snippet of article",
      byline: { original: "By Author" },
      pub_date: "2025-05-01T12:00:00Z",
      web_url: "article_link.com"
    }
  ]

  const { getByText } = render(App, { props: { articles: articles } });

  expect(getByText("Title")).toBeTruthy();
  expect(getByText("This is snippet of article")).toBeTruthy();
  expect(getByText("By Author")).toBeTruthy();
  expect(getByText("Published on: 5/1/2025")).toBeTruthy();
})

test("Test Date at header", () => {
  const { getByText } = render(App);
  const today_date = getDate();
  expect(getByText(today_date)).toBeTruthy();
})

test("Test for NYT article format provided by backend", async () => {
  const articles = await getArticles();
  const article = articles[0];
  if (article) {
    expect("url").toBeInstanceOf(article.multimedia.default);
    expect("caption").toBeInstanceOf(article.multimedia);
    expect("main").toBeInstanceOf(article.headline);
    expect("snippet").toBeInstanceOf(article);
    expect("original").toBeInstanceOf(article.byline);
    expect("pub_date").toBeInstanceOf(article);
    expect("web_url").toBeInstanceOf(article);
  }
})

