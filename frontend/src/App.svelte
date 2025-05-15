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
      <li class="nav-item"><a href="https://www.nytimes.com/section/us" target="_blank" rel="noopener noreferrer">U.S.</a></li>
      <li class="nav-item"><a href="https://www.nytimes.com/section/world" target="_blank" rel="noopener noreferrer">World</a></li>
      <li class="nav-item"><a href="https://www.nytimes.com/section/business" target="_blank" rel="noopener noreferrer">Business</a></li>
      <li class="nav-item"><a href="https://www.nytimes.com/section/arts" target="_blank" rel="noopener noreferrer">Arts</a></li>
      <li class="nav-item"><a href="https://www.nytimes.com/section/style" target="_blank" rel="noopener noreferrer">Lifestyle</a></li>
      <li class="nav-item"><a href="https://www.nytimes.com/section/opinion" target="_blank" rel="noopener noreferrer">Opinion</a></li>
      <li class="nav-item"><a href="https://www.nytimes.com/section/audio" target="_blank" rel="noopener noreferrer">Audio</a></li>
      <li class="nav-item"><a href="https://www.nytimes.com/crosswords" target="_blank" rel="noopener noreferrer">Games</a></li>
      <li class="nav-item"><a href="https://cooking.nytimes.com/" target="_blank" rel="noopener noreferrer">Cooking</a></li>
      <li class="nav-item"><a href="https://www.nytimes.com/wirecutter/" target="_blank" rel="noopener noreferrer">Wirecutter</a></li>
      <li class="nav-item"><a href="https://www.theatlantic.com/" target="_blank" rel="noopener noreferrer">Atlantic</a></li>
    </ul>
  </nav>
  <hr/>
  <hr/>
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