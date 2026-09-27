import { mount } from 'svelte';
import App from './App.svelte';
import './simple.css';
import './quiz-interaction.css';

mount(App, {
  target: document.getElementById('app'),
});