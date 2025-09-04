<script lang="ts">
	import ImageSkeleton from '$lib/simpleComponent/ImageSkeleton.svelte';
	import { onMount } from 'svelte';

	const {
		src,
		alt,
		skeleton = false,
		class: classes = '',
		aspectRatio = 'aspect-1920/1080',
		name
	} = $props();

	let img: HTMLImageElement | null = $state(null);

	let isLoaded = $state(false);
	let onload = $state(() => {
		isLoaded = true;
	});

	onMount(() => {
		if (!skeleton) {
			getImage();
		}
	});

	export function getImage() {
		isLoaded = false;
		// I don't know why, but this setTimeout is necessary to make the image update
		// without it, the image will not update and stay as the old image
		setTimeout(() => {
			img = new Image();
			img.src = src;
		}, 0);
	}

	function saveToDisk() {
		if (img) {
			const link = document.createElement('a');
			link.href = img.src;
			link.download = name + '.png';
			link.target = '_blank';
			link.click();
		}
	}
</script>

{#if !skeleton}
<!-- TODO : Change that without breaking the layout -->
	<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<img
		src={src}
		{onload}
		{alt}
		class="peer rounded-lg xl:max-h-full cursor-pointer {classes} {!isLoaded ? 'hidden' : ''}"
		onclick={saveToDisk}
	/>
{/if}
{#if skeleton || !isLoaded}
	<ImageSkeleton aspectratio={aspectRatio} />
{/if}
