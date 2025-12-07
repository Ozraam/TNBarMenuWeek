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

	const width = layout.image_size[0];
	const height = layout.image_size[1];
	const grid = layout.grid;
	const contentSpacing = layout.content_spacing || 30;

	let headerGap = 0;
	let headerInnerGap = 0;
	let cellPaddingY = 6;
	let itemsGap = 0;
	let textMarginBottom = 0;
	const gridWidth = grid.cell_width * grid.cols;
	const gridTopMargin = grid.y_start || 0;
	let imageWidth = 250;
	let imageTitleGap = 0;
	let cellPaddingBottom = 0;
	let cellPaddingX = 0;

	if (layoutName === 'horizontal') {
		headerGap = Math.max(10, contentSpacing / 3);
		headerInnerGap = Math.max(8, headerGap / 2);
		imageWidth = Math.min(250, Math.max(140, grid.cell_width * 0.55));
		itemsGap = Math.max(8, contentSpacing / 3);
		textMarginBottom = Math.max(6, contentSpacing / 4);
		cellPaddingY = Math.max(8, headerGap / 3);
		imageTitleGap = 2;
		cellPaddingBottom = cellPaddingY + 12;
		cellPaddingX = Math.max(16, grid.cell_width / 12);
	}

	function getCellBackground(index: number): string {
		const row = Math.floor(index / grid.cols);
		const col = index % grid.cols;
		return (row + col) % 2 === 0 ? colors.primary : colors.secondary;
	}

	function getWeekAnchorStyle(): string {
		const [x, y] = layout.week_text_position;
		const anchor = layout.week_text_anchor || 'lt';

		const transforms: string[] = [];
		const horizontal = anchor[0] || 'l';
		const vertical = anchor[1] || 't';

		if (horizontal === 'm') {
			transforms.push('translateX(-50%)');
		} else if (horizontal === 'r') {
			transforms.push('translateX(-100%)');
		}

		if (vertical === 'm') {
			transforms.push('translateY(-50%)');
		} else if (vertical === 'b') {
			transforms.push('translateY(-100%)');
		}

		const transformStyle = transforms.length ? `transform: ${transforms.join(' ')};` : '';
		return `left: ${x}px; top: ${y}px; ${transformStyle}`;
	}
</script>

<div
	class="menu-container {className}"
	style:width="{width}px"
	style:height="{height}px"
	style:background={colors.background}
>
	<img class="menu-logo" src={logoPath} alt="Logo" />
	<div
		class="menu-title"
		style:left="{layout.title_position[0]}px"
		style:top="{layout.title_position[1]}px"
		style:font-size="{layout.title_font_size}px"
		style:color={colors.secondary}
	>
		{@html layout.title_text.replace(/\n/g, '<br>')}
	</div>
	<div
		class="menu-week"
		style={getWeekAnchorStyle()}
		style:font-size="{layout.week_font_size}px"
		style:color={colors.primary}
	>
		{@html weekText.replace(/\n/g, '<br>')}
	</div>
	<div
		class="menu-grid"
		style:margin-top="{gridTopMargin}px"
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
								{#if item.img}
									<img
										src="/Sandwichlogo/{item.img}.png"
										alt={item.img}
										style:width="{imageWidth}px"
									/>
								{/if}
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
		position: relative;
		overflow: hidden;
		font-family: 'MenuFont', 'Open Sans', sans-serif;
	}

	.menu-logo {
		position: absolute;
		left: 10px;
		top: 10px;
		width: 360px;
		height: auto;
	}

	.menu-title {
		position: absolute;
		font-weight: 700;
		line-height: 1.05;
		text-align: center;
		white-space: pre-line;
	}

	.menu-week {
		width: max-content;
		position: absolute;
		font-weight: 600;
		text-transform: uppercase;
		line-height: 1.1;
		text-align: center;
		white-space: pre-line;
	}

	.menu-grid {
		position: relative;
		margin-left: auto;
		margin-right: auto;
		display: grid;
		justify-content: center;
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
