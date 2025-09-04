<script lang="ts">
	import { fade, fly } from 'svelte/transition';
	import { loadingState } from './loadingState.svelte';
    import { onMount, onDestroy } from 'svelte';

    const loadingText = [
        "Generating images...",
        "This can take a while...",
        "Please wait...",
        "Up to 2 minutes...",
        "Almost there...",
    ]
    let textIndex = 0;

    onMount(() => {
        const interval = setInterval(() => {
            textIndex = (textIndex + 1) % loadingText.length;
        }, 7000);

        onDestroy(() => {
            clearInterval(interval);
        });
    });

    function flyAbsolute(node: HTMLElement, params: { delay?: number, duration?: number, easing?: (t: number) => number, y?: number }) {
        return {
            delay: params.delay || 0,
            duration: params.duration || 400,
            easing: params.easing || ((t: number) => t),
            css: (t: number) => {
                const style = getComputedStyle(node);
                const transform = style.transform === 'none' ? '' : style.transform;
                const opacity = +style.opacity;
                const y = (params.y ?? 0) * (1 - t);
                return `
                    position: absolute;
                    transform: ${transform} translateY(${y}px);
                    opacity: ${t * opacity};
                `;
            }
        };
    }
</script>

<div class="absolute left-1/2 -translate-x-1/2 bottom-10 bg-gray-800 p-2 rounded-full flex gap-3 transition-transform {loadingState.loading ? "" : "translate-y-32"} duration-500 ease-in-out">
	<div
		class="grid place-items-center rounded-lg lg:overflow-visible"
	>
		<svg
			class="animate-spin text-gray-300"
			viewBox="0 0 64 64"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
			width="24"
			height="24"
		>
			<path
				d="M32 3C35.8083 3 39.5794 3.75011 43.0978 5.20749C46.6163 6.66488 49.8132 8.80101 52.5061 11.4939C55.199 14.1868 57.3351 17.3837 58.7925 20.9022C60.2499 24.4206 61 28.1917 61 32C61 35.8083 60.2499 39.5794 58.7925 43.0978C57.3351 46.6163 55.199 49.8132 52.5061 52.5061C49.8132 55.199 46.6163 57.3351 43.0978 58.7925C39.5794 60.2499 35.8083 61 32 61C28.1917 61 24.4206 60.2499 20.9022 58.7925C17.3837 57.3351 14.1868 55.199 11.4939 52.5061C8.801 49.8132 6.66487 46.6163 5.20749 43.0978C3.7501 39.5794 3 35.8083 3 32C3 28.1917 3.75011 24.4206 5.2075 20.9022C6.66489 17.3837 8.80101 14.1868 11.4939 11.4939C14.1868 8.80099 17.3838 6.66487 20.9022 5.20749C24.4206 3.7501 28.1917 3 32 3L32 3Z"
				stroke="currentColor"
				stroke-width="5"
				stroke-linecap="round"
				stroke-linejoin="round"
			></path>
			<path
				d="M32 3C36.5778 3 41.0906 4.08374 45.1692 6.16256C49.2477 8.24138 52.7762 11.2562 55.466 14.9605C58.1558 18.6647 59.9304 22.9531 60.6448 27.4748C61.3591 31.9965 60.9928 36.6232 59.5759 40.9762"
				stroke="currentColor"
				stroke-width="5"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="text-violet-500"
			>
			</path>
		</svg>
	</div>

    <div class="relative">
        {#each loadingText as text, i}
            {#if i === textIndex}
                <p class="text-gray-300 text-sm {i != textIndex ? "absolute" : ""}" in:fly={{ y: 10, duration: 300 }} out:flyAbsolute={{ y: -10, duration: 200 }}>
                    {text}
                </p>
            {/if}
        {/each}
    </div>
</div>
