<script lang="ts">
	import type { DayOptions } from '../type';
	import SpaceConfiguration from './SpaceConfiguration.svelte';

	const {
		label,
        key,
		space = $bindable([]),
		mealList = [],
		class: class_ = '',
	}: {
		label: string;
        key: string;
		space: DayOptions[];
		mealList: {
			name: string;
			image: string;
		}[];
		class: string;
	} = $props();

	/**
	 * Effect block to ensure that if the first space is not used,
	 * the second space is also not used.
	 */
	$effect(() => {
		if (!space[0].is_used) {
			space[1].is_used = false;
		}
	});
</script>

<div class={class_}>
	<h3 class="capitalize font-bold text-lg">
		{label}
	</h3>
	<SpaceConfiguration label="Utiliser l'emplacement haut" key="{key}-space-1" bind:space={space[0]} class="w-full" {mealList} />
	{#if space[0].is_used}
		<SpaceConfiguration label="Utiliser l'emplacement bas" key="{key}-space-2" bind:space={space[1]} class="mt-2" {mealList} />
	{/if}
</div>
