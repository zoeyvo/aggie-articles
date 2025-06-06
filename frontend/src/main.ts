import { mount } from 'svelte'
import './app.scss'
import './script'
import App from './App.svelte'

const app = mount(App, {
  target: document.getElementById('app')!,
})

export default app