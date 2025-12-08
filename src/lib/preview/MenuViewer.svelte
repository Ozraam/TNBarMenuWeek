<script lang="ts">
	import { MenuRenderer } from '$lib/menuRenderer';
	import ImageSkeleton from '$lib/simpleComponent/ImageSkeleton.svelte';
	import type { MenuCell, MenuLayoutConfig, MenuColors } from '$lib/menuRenderer/types';

	interface Props {
		layoutName: 'vertical' | 'horizontal';
		layout: MenuLayoutConfig;
		colors: MenuColors;
		weekText: string;
		cells: MenuCell[];
		logoPath: string;
		skeleton?: boolean;
		aspectRatio?: string;
		class?: string;
		name: string;
	}

	let {
		layoutName,
		layout,
		colors,
		weekText,
		cells,
		logoPath,
		skeleton = false,
		aspectRatio = 'aspect-1920/1080',
		class: classes = '',
		name
	}: Props = $props();

	let menuContainer: HTMLDivElement;

	async function downloadAsImage() {
		if (!menuContainer) return;

		// Dynamically import html2canvas only when needed
		const html2canvas = (await import('html2canvas')).default;

		const canvas = await html2canvas(menuContainer, {
			backgroundColor: colors.background,
			scale: 2, // Higher quality
			logging: false,
			useCORS: true,
			allowTaint: true
		});

		// Convert canvas to blob and download
		canvas.toBlob((blob) => {
			if (blob) {
				const url = URL.createObjectURL(blob);
				const link = document.createElement('a');
				link.href = url;
				link.download = `${name}.png`;
				link.click();
				URL.revokeObjectURL(url);
			}
		});
	}
</script>

{#if !skeleton}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="menu-viewer-wrapper rounded-lg xl:max-h-full cursor-pointer {classes}"
		onclick={downloadAsImage}
		style="aspect-ratio: {layout.image_size[0]} / {layout.image_size[1]};"
	>
		<div bind:this={menuContainer} class="menu-content">
			<MenuRenderer {layoutName} {layout} {colors} {weekText} {cells} {logoPath} />
		</div>
	</div>
{/if}
{#if skeleton}
	<ImageSkeleton aspectratio={aspectRatio} />
{/if}

<style>
	.menu-viewer-wrapper {
		position: relative;
		width: 100%;
		overflow: hidden;
		background: white;
	}

	.menu-content {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.menu-content :global(.menu-container) {
		max-width: 100%;
		max-height: 100%;
		width: auto;
		height: auto;
	}
</style>
