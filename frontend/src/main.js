import { mount } from 'svelte';
import App from './App.svelte';
import Login from './Login.svelte';
import './simple.css';
import './quiz-interaction.css';

mount(window.location.pathname === '/login' ? Login : App, {
  target: document.getElementById('app'),
});