<script lang="ts">
  import { onMount } from "svelte";
  import nytLogo from "./assets/nyt-logo.png";
  import { getDate, getArticles } from "./script";

  export let date_display = getDate();

  export let articles: any[] = [];
  onMount(async () => {
    // Articles fetched using backend API route in app.py
    articles = await getArticles();
  });
</script>

<header>
  <div class="header-container">
    <!-- logo image and dynamic date -->
    <img src={nytLogo} alt="The New York Times" />
    <div id="current-date">{date_display}</div>
  </div>
  <nav class="main-nav">
    <ul>
      <!-- list of potential pages -->
      <li class="nav-item"><a href="#">U.S.</a></li>
      <li class="nav-item"><a href="#">World</a></li>
      <li class="nav-item"><a href="#">Business</a></li>
      <li class="nav-item"><a href="#">Arts</a></li>
      <li class="nav-item"><a href="#">Lifestyle</a></li>
      <li class="nav-item"><a href="#">Opinion</a></li>
      <li class="nav-item"><a href="#">Audio</a></li>
      <li class="nav-item"><a href="#">Games</a></li>
      <li class="nav-item"><a href="#">Cooking</a></li>
      <li class="nav-item"><a href="#">Wirecutter</a></li>
      <li class="nav-item"><a href="#">Atlantic</a></li>
    </ul>
  </nav>
</header>
<hr />
<hr />
<main>
  <!-- Main content displayed as a media-responsive grid -->
  <!-- Iterate over retrieved articles -->
  {#each articles as article}
    <article>
      <img
        src={article.multimedia.default.url}
        alt={article.multimedia.caption}
      />
      <h2>{article.headline.main}</h2>
      <p>{article.snippet}</p>
      <p>{article.byline.original}</p>
      <p>Published on: {new Date(article.pub_date).toLocaleDateString()}</p>
      <a href={article.web_url} target="_blank" class="read-more">Read more</a>
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