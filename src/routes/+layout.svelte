<script lang="ts">
	import { classList } from '$lib/classList';
	import '../app.css';
	let { children } = $props();

	
</script>

<svelte:body use:classList={["h-screen", "flex", "flex-col", "bg-linear-to-bl", "from-orange-800", "to-blue-600", "text-white", "overflow-hidden", "p-3", "gap-3"]} />

<header class="flex justify-between p-3 bg-gray-600/20 rounded-lg bg-clip-padding backdrop-filter backdrop-blur-md bg-opacity-20 border border-gray-100 to-">
    <h1>
        Menu Generator
    </h1>

    <nav>
        <ul class="flex gap-6">
            <li class="hover:text-orange-500 transition-all duration-100">
                <a href="/">Home</a>
            </li>
            <li class="hover:text-orange-500 transition-all duration-100">
                <a href="/newSandwich">Ajouter Sandwich</a>
            </li>
            <li class="hover:text-orange-500 transition-all duration-100">
                <a href="/about">About</a>
            </li>
        </ul>
    </nav>
</header>

{@render children()}
