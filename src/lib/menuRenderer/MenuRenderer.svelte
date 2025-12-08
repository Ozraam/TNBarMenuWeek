<script lang="ts">
	import type { MenuCell, MenuLayoutConfig, MenuColors } from './types';

	interface Props {
		layoutName: 'vertical' | 'horizontal';
		layout: MenuLayoutConfig;
		colors: MenuColors;
		weekText: string;
		cells: MenuCell[];
		logoPath: string;
		class?: string;
	}

	let { layoutName, layout, colors, weekText, cells, logoPath, class: className }: Props = $props();

	// Use $derived for computed values that depend on props
	const width = $derived(layout.image_size[0]);
	const height = $derived(layout.image_size[1]);
	const grid = $derived(layout.grid);
	const contentSpacing = $derived(layout.content_spacing || 30);
	const gridWidth = $derived(grid.cell_width * grid.cols);

	// Compute layout-specific values
	const headerGap = $derived(
		layoutName === 'horizontal' ? Math.max(10, contentSpacing / 3) : 0
	);
	const headerInnerGap = $derived(
		layoutName === 'horizontal' ? Math.max(8, headerGap / 2) : 0
	);
	const cellPaddingY = $derived(
		layoutName === 'horizontal' ? Math.max(8, headerGap / 3) : 6
	);
	const itemsGap = $derived(
		layoutName === 'horizontal' ? Math.max(8, contentSpacing / 3) : 0
	);
	const textMarginBottom = $derived(
		layoutName === 'horizontal' ? Math.max(6, contentSpacing / 4) : 0
	);
	const imageWidth = $derived(
		layoutName === 'horizontal' 
			? Math.min(250, Math.max(140, grid.cell_width * 0.55))
			: 250
	);
	const imageTitleGap = $derived(layoutName === 'horizontal' ? 2 : 0);
	const cellPaddingBottom = $derived(
		layoutName === 'horizontal' ? cellPaddingY + 12 : 0
	);
	const cellPaddingX = $derived(
		layoutName === 'horizontal' ? Math.max(16, grid.cell_width / 12) : 0
	);

	function getCellBackground(index: number): string {
		const row = Math.floor(index / grid.cols);
		const col = index % grid.cols;
		return (row + col) % 2 === 0 ? colors.primary : colors.secondary;
	}
</script>

<div
	class="menu-container {className}"
	style:width="{width}px"
	style:height="{height}px"
	style:background={colors.background}
>
	<div class="menu-header">
		<img class="menu-logo" src={logoPath} alt="Logo" />
		<div class="menu-header-text">
			<div
				class="menu-title"
				style:font-size="{layout.title_font_size}px"
				style:color={colors.secondary}
			>
				{@html layout.title_text.replace(/\n/g, '<br>')}
			</div>
			<div
				class="menu-week"
				style:font-size="{layout.week_font_size}px"
				style:color={colors.primary}
			>
				{@html weekText.replace(/\n/g, '<br>')}
			</div>
		</div>
	</div>
	<div
		class="menu-grid"
		style:width="{gridWidth}px"
		style:grid-template-columns="repeat({grid.cols}, {grid.cell_width}px)"
		style:grid-auto-rows="{grid.cell_height}px"
	>
		{#each cells as cell, index}
			<div
				class="menu-cell"
				style:background={getCellBackground(index)}
				style:padding="{cellPaddingY}px {cellPaddingX}px {cellPaddingBottom}px"
				style:gap="{headerGap}px"
				style:font-size="{layout.content_font_size}px"
				style:color={colors.text}
			>
				<div class="day-header" style:gap="{headerInnerGap}px">
					<div class="separator" style:background={colors.background}></div>
					<div class="label" style:font-size="{layout.day_font_size}px">
						{cell.label.toUpperCase()}
					</div>
					<div class="separator" style:background={colors.background}></div>
				</div>
				<div class="items" style:gap="{itemsGap}px">
					{#each cell.items as item}
						<div class="item {item.is_meal ? 'meal' : 'note'}" style:gap="{imageTitleGap}px">
							{#if item.is_meal && item.img}
								{@const customImages = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('customImages') || '{}') : {}}
								{@const imageSource = customImages[item.img] || `/Sandwichlogo/${item.img}.png`}
								<img
									src={imageSource}
									alt={item.img}
									style:width="{imageWidth}px"
								/>
							{/if}
							<div class="item-text" style:margin-bottom="{textMarginBottom}px">
								{@html item.text.replace(/\n/g, '<br>')}
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	@font-face {
		font-family: 'MenuFont';
		src: url('/OpenSans-VariableFont_wdth,wght.ttf') format('truetype');
		font-display: swap;
	}

	.menu-container {
		display: flex;
		flex-direction: column;
		overflow: hidden;
		font-family: 'MenuFont', 'Open Sans', sans-serif;
	}

	.menu-header {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 10px;
		gap: 20px;
	}

	.menu-logo {
		width: 360px;
		height: auto;
		flex-shrink: 0;
	}

	.menu-header-text {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 15px;
	}

	.menu-title {
		font-weight: 700;
		line-height: 1.05;
		text-align: center;
		white-space: pre-line;
	}

	.menu-week {
		font-weight: 600;
		text-transform: uppercase;
		line-height: 1.1;
		text-align: center;
		white-space: pre-line;
	}

	.menu-grid {
		display: grid;
		justify-content: center;
		margin: 0 auto;
		flex: 1;
	}

	.menu-cell {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: flex-start;
		box-sizing: border-box;
	}

	.day-header {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.day-header .separator {
		width: calc(100% - 20px);
		height: 5px;
		border-radius: 3px;
	}

	.day-header .label {
		text-align: center;
		font-weight: 800;
		letter-spacing: 1px;
	}

	.items {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.item {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		width: 100%;
	}

	.item-text {
		white-space: pre-line;
		line-height: 1.2;
		font-weight: 600;
		margin-left: auto;
		margin-right: auto;
	}

	.item.meal img {
		height: auto;
		border-radius: 12px;
		object-fit: contain;
	}

	.item.note .item-text {
		font-style: italic;
	}
</style>
