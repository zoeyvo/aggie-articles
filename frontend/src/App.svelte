<script lang="ts">
  import { onMount } from "svelte";
  import nytLogo from "./assets/nyt-logo.png";
  import {
    fetchComments,
    submitComment,
    replyComment,
    moderateComment,
    fetchReplies,
    getDate,
    getArticles,
    getAuthenticatedUser,
  } from "./script";

  export let date_display = getDate();

  // Authentication data
  let user = {
    authenticated: false,
    username: "",
    email: "",
    user_id: "",
  };

  // Articles array to store fetched articles
  export let articles: any[] = [];

  // Store to track which articles have comments visible
  let articleCommentsVisible: { [key: string]: boolean } = {};

  // Store comments for each article
  let articleComments: { [key: string]: any[] } = {};

  let articlesReplies: { [key: string]: any[] } = {};

  // Track new comment input for each article
  let newCommentText: { [key: string]: string } = {};

  // Get a stable article ID suitable for comments
  function getArticleIdentifier(article: any): string {
    // First check if article has a URL with the nyt:// pattern
    if (article.web_url && article.web_url.includes("nyt://")) {
      console.log(`Using web_url as ID: ${article.web_url}`);
      return article.web_url;
    }
    // Otherwise fallback to the article's MongoDB ID
    console.log(`Using _id as ID: ${article._id}`);
    return article._id;
  }

  // Toggle comments visibility for a specific article
  async function toggleComments(article: any) {
    const articleId = getArticleIdentifier(article);

    // Lazy load comments when showing them for the first time
    if (articleComments[articleId].length === 0) {
      reloadComments(articleId);
    }

    articleCommentsVisible[articleId] = !articleCommentsVisible[articleId];
  }

  // Add a new comment to an article
  async function addNewComment(article: any) {
    const articleId = getArticleIdentifier(article);

    if (newCommentText[articleId]?.trim()) {
      const success = await submitComment(articleId, newCommentText[articleId]);

      if (success) {
        // Refresh comments after successful submission
        reloadComments(articleId);

        // Clear the input field
        newCommentText[articleId] = "";
      }
    }
  }

  let newReplyText: { [key: string]: string } = {};
  let showReplyField: { [key: string]: boolean } = {};

  function openReplyField(commentID: any) {
    showReplyField[commentID] = !showReplyField[commentID];
  }

  async function addReply(article: any, parentID: any) {
    const articleId = getArticleIdentifier(article);

    if (newReplyText[parentID]?.trim()) {
      const success = await replyComment(
        articleId,
        parentID,
        newReplyText[parentID],
      );

      if (success) {
        reloadComments(articleId);

        newReplyText[parentID] = "";
        showReplyField[parentID] = false;
      }
    }
  }

  async function reloadComments(articleId: any) {
    const updatedComments = await fetchComments(articleId);

    let rootComments = [];
    // let replies: { [key: string]: any[] } = {};

    for (const comment of updatedComments) {
      if (!("parentID" in comment)) {
        rootComments.push(comment);
      }
    }
    articleComments[articleId] = rootComments;

    for (const comment of rootComments) {
      const replies = await fetchReplies(comment._id);
      articlesReplies[comment._id] = replies;
    }
  }

  onMount(async () => {
    // Get authentication status
    user = await getAuthenticatedUser();
    console.log(
      "Authentication status:",
      user.authenticated ? "Logged in" : "Not logged in",
    );

    // Articles fetched using backend API route in app.py
    articles = await getArticles();

    // Log the first article to see its structure
    if (articles.length > 0) {
      console.log("First article structure:", articles[0]);
      console.log("Article URL:", articles[0].web_url);
    }

    // Initialize comment tracking for each article
    articles.forEach((article) => {
      const articleId = getArticleIdentifier(article);
      articleCommentsVisible[articleId] = false;
      articleComments[articleId] = [];
      newCommentText[articleId] = "";
    });
  });
</script>

<header>
  <div class="header-container">
    <!-- logo image and dynamic date -->
    <img src={nytLogo} alt="The New York Times" />
    <div id="current-date">{date_display}</div>
    {#if user.authenticated === false}
      <a href="/login"><button class="login_btn">Log In</button></a>
    {:else}
      <div class="login_info">
        <div>Hello, {user.username}</div>
        <a href="/logout"><button class="login_btn">Log Out</button></a>
      </div>
    {/if}
  </div>
  <nav class="main-nav">
    <ul>
      <!-- No authentication status, always show nav links -->
      <li class="nav-item">
        <a
          href="https://www.nytimes.com/section/us"
          target="_blank"
          rel="noopener noreferrer">U.S.</a
        >
      </li>
      <li class="nav-item">
        <a
          href="https://www.nytimes.com/section/world"
          target="_blank"
          rel="noopener noreferrer">World</a
        >
      </li>
      <li class="nav-item">
        <a
          href="https://www.nytimes.com/section/business"
          target="_blank"
          rel="noopener noreferrer">Business</a
        >
      </li>
      <li class="nav-item">
        <a
          href="https://www.nytimes.com/section/arts"
          target="_blank"
          rel="noopener noreferrer">Arts</a
        >
      </li>
      <li class="nav-item">
        <a
          href="https://www.nytimes.com/section/style"
          target="_blank"
          rel="noopener noreferrer">Lifestyle</a
        >
      </li>
      <li class="nav-item">
        <a
          href="https://www.nytimes.com/section/opinion"
          target="_blank"
          rel="noopener noreferrer">Opinion</a
        >
      </li>
      <li class="nav-item">
        <a
          href="https://www.nytimes.com/section/audio"
          target="_blank"
          rel="noopener noreferrer">Audio</a
        >
      </li>
      <li class="nav-item">
        <a
          href="https://www.nytimes.com/crosswords"
          target="_blank"
          rel="noopener noreferrer">Games</a
        >
      </li>
      <li class="nav-item">
        <a
          href="https://cooking.nytimes.com/"
          target="_blank"
          rel="noopener noreferrer">Cooking</a
        >
      </li>
      <li class="nav-item">
        <a
          href="https://www.nytimes.com/wirecutter/"
          target="_blank"
          rel="noopener noreferrer">Wirecutter</a
        >
      </li>
      <li class="nav-item">
        <a
          href="https://www.theatlantic.com/"
          target="_blank"
          rel="noopener noreferrer">Atlantic</a
        >
      </li>
    </ul>
  </nav>
  <hr />
  <hr />
</header>
<main>
  <!-- Main content displayed as a media-responsive grid -->
  <!-- Iterate over retrieved articles -->
  {#each articles as article}
    <article>
      <img
        src={article.multimedia.default.url}
        alt={article.multimedia.caption}
      />
      <h2><strong>{article.headline.main}</strong></h2>
      <p>{article.snippet}</p>
      <p><u>{article.byline.original}</u></p>
      <p>
        <em>Published on: {new Date(article.pub_date).toLocaleDateString()}</em>
      </p>
      <a href={article.web_url} target="_blank" class="read-more">Read more</a>
      <div class="comment-controls">
        <button on:click={() => toggleComments(article)}>
          {articleCommentsVisible[getArticleIdentifier(article)]
            ? "Hide Comments"
            : "Show Comments"}
        </button>
      </div>
      {#if articleCommentsVisible[getArticleIdentifier(article)]}
        <div class="comments-section">
          <h4>Comments</h4>
          <!-- Display comments if there are any -->
          {#if articleComments[getArticleIdentifier(article)]?.length > 0}
            <div class="comments-list">
              {#each articleComments[getArticleIdentifier(article)] as comment}
                <div class="comment">
                  <p>
                    <strong>{comment.username || "Anonymous"}</strong>: {comment.text}
                  </p>
                  <div>
                    {#if user.authenticated === true}
                      <button
                        class="reply_btn"
                        on:click={() => openReplyField(comment._id)}
                      >
                        {showReplyField[comment._id] ? "Hide Replies" : "Reply"}
                      </button>
                      {#if showReplyField[comment._id]}
                        <div class="new_reply">
                          <input
                            type="text"
                            placeholder="Add a reply..."
                            bind:value={newReplyText[comment._id]}
                          />
                          <button
                            on:click={() => addReply(article, comment._id)}
                          >
                            Reply
                          </button>
                        </div>
                      {/if}
                    {/if}
                    {#if user.email === "admin@hw3.com" || user.email === "moderator@hw3.com"}
                      <button
                        class="delete_btn"
                        on:click={() => {
                          moderateComment(comment._id);
                          reloadComments(getArticleIdentifier(article));
                        }}
                      >
                        Delete
                      </button>
                    {/if}
                  </div>
                  {#each articlesReplies[comment._id] as reply}
                    <div class="reply">
                      | <strong>{comment.username || "Anonymous"}</strong>: {reply.text}
                    </div>
                    {#if user.email === "admin@hw3.com" || user.email === "moderator@hw3.com"}
                      <button
                        class="delete_btn"
                        on:click={() => {
                          moderateComment(reply._id);
                          reloadComments(getArticleIdentifier(article));
                        }}
                      >
                        Delete
                      </button>
                    {/if}
                  {/each}
                </div>
              {/each}
            </div>
          {:else}
            <p class="no-comments">No comments yet. Be the first to comment!</p>
          {/if}
          <!-- New comment input and submission: always show since login is forced -->
          {#if user.authenticated === true}
            <div class="new-comment">
              <input
                type="text"
                placeholder="Add a comment..."
                bind:value={newCommentText[getArticleIdentifier(article)]}
              />
              <button on:click={() => addNewComment(article)}>Submit</button>
            </div>
          {:else}
            <div>You need to log in to comment</div>
          {/if}
        </div>
      {/if}
    </article>
  {/each}
</main>
<footer>
  <!-- footer for additonal information -->
  <div class="footer-content">
    <p>
      <!-- CSS validator pass -->
      <a href="https://jigsaw.w3.org/css-validator/check/referer">
        <img
          style="border:0;width:88px;height:31px"
          src="https://jigsaw.w3.org/css-validator/images/vcss"
          alt="Valid CSS!"
        />
      </a>
    </p>
    <p>&copy; 2025 The New York Times</p>
    <p>Zoey Vo, Loc Nguyen</p>
  </div>
</footer>
