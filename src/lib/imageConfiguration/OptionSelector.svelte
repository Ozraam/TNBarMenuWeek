<script lang="ts">
	import WeekIndication from './WeekIndication.svelte';
	import DayOption from './DayOption.svelte';
	import type { DayOptions } from '../type';
	import { imgLinkState, loadingState } from '$lib/loadingState.svelte';
	import { onMount } from 'svelte';
	import { json } from '@sveltejs/kit';

	const {
		class: class_ = '',
		children,
		onclick = () => {},
		imageGeneratedCallback = () => {}
	} = $props();
	
	let contentDiv = $state<HTMLElement | null>(null);
	let weekOption: { label: string; space: DayOptions[] }[] = $state([]);

	/**
	 * Sets up the week options based on the provided data.
	 * @param data - The data containing header and content for each day.
	 */
	function setupWeekOption(data: { header: string[]; content: any[] }) {
		weekOption = data['header'].map((day: string, index: number) => {
			let space : any[] = data['content'][index]['content'].map((space: any) => {
				return {
					is_used: true,
					is_meal: space['is_meal'],
					text: space['text'],
					meal: space['img'] || undefined
				};
			});

            space = space.concat(Array(2 - space.length).fill(0).map(() => {
                return {
                    is_used: false,
                    is_meal: true,
                    text: '',
                    meal: undefined
                };
            }));

			return {
				label: day,
				space: space
			};
		});
	}

	const customTextFrench = 'Voici le menu de cette semaine !';
	const customTextEnglish = 'Here is the menu for this week!';

	let mealList: {
		name: string;
		image: string;
	}[] = $state([]);

	onMount(() => {
		fetch('http://localhost:5000/getMealList', {
			method: 'GET'
		}).then((data) => {
			if (data.ok) {
				data.json().then((mealListAPI) => {
					mealList = mealListAPI;
				});
			} else {
				alert('An error occured');
			}
		});

		fetch('http://localhost:5000/getLastMenu', {
			method: 'GET'
		}).then(async (data) => {
			if (data.ok) {
				const json = await data.json();
				setupWeekOption(json);
			} else {
				weekOption = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'pub'].map((day) => {
					return {
						label: day,
						space: Array(2)
							.fill(0)
							.map(() => {
								return {
									is_used: false,
									is_meal: true,
									text: '',
									meal: undefined
								};
							})
					};
				});
			}
		});
	});

	function getMealText(meal: string) {
		return mealList.find((mealOption: any) => mealOption.image === meal)?.name || '';
	}

	/**
	 * Converts the week options to a CLI command string.
	 * @returns The CLI command string.
	 */
	function weekOptionToCLI() {
		let cli = `--header ${weekOption
			.map((day) => {
				return day.label;
			})
			.join(
					' '
			)} --custom-text-french "${customTextFrench}" --custom-text-english "${customTextEnglish}" `;

		cli += weekOption
			.map((day) => {
				let dayCLI = `--content --day ${day.label} --day-content ${day.space
					.filter((space) => space.is_used)
					.map((space) => {
						return `${space.is_meal ? '--is-meal ' : ''}--text "${space.is_meal ? getMealText(space.meal!) : space.text}" ${space.is_meal ? `--img ${space.meal} ` : ''}`.trim();
					})
					.filter((s) => s.length != 0)
					.join(' ')}`.trim();

				return dayCLI;
			})
			.join(' ');

		return cli;
	}

	/**
	 * Generates images based on the current week options.
	 */
	function generateImage() {
		let cli = weekOptionToCLI();
		fetch('http://localhost:5000/generateImages?menu=' + cli, {
			method: 'GET'
		}).then(async (data) => {
			if (data.ok) {
				const josn = await data.json()
				imgLinkState.horizontal = josn.horizontal
				imgLinkState.vertical = josn.vertical
				imageGeneratedCallback();
			} else {
				loadingState.loading = false;
				alert('An error occured');
			}
		});
		onclick();
		contentDiv?.scrollTo(0, 0);
	}

</script>

<div
	bind:this={contentDiv}
	class="rounded-lg border border-gray-100 bg-gray-600/20 bg-clip-padding backdrop-blur-md backdrop-filter {class_}"
>
	{@render children()}

	<div class="flex justify-between gap-7">
		<h2 class="text-xl font-bold">Customization</h2>

		<WeekIndication />
	</div>

		{#each weekOption as dayOption, i}
			<DayOption
				label={dayOption.label}
				key={dayOption.label}
				bind:space={dayOption.space}
				{mealList}
				class="w-full"
			/>

			{#if i < weekOption.length - 1}
				<div class="border-t border-white/25"></div>
			{/if}
		{/each}
	

	<button
		onclick={() => {
			loadingState.loading = true;
			generateImage();
		}}
		class="mx-auto mt-3 flex items-center rounded-md border border-transparent bg-slate-800 px-4 py-2 text-center text-sm text-white shadow-sm transition-all hover:bg-slate-700 hover:shadow-lg focus:bg-slate-700 focus:shadow-none active:bg-slate-700 active:shadow-none disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none"
		type="button"
	>
		<svg xmlns="http://www.w3.org/2000/svg" class="mr-1.5 h-4 w-4" viewBox="0 0 24 24"
			><path
				fill="currentColor"
				d="m5.85 12l-.3-1.5q-.3-.125-.562-.262T4.45 9.9L3 10.35l-1-1.7l1.15-1Q3.1 7.325 3.1 7t.05-.65L2 5.35l1-1.7l1.45.45q.275-.2.538-.338T5.55 3.5l.3-1.5h2l.3 1.5q.3.125.563.263t.537.337l1.45-.45l1 1.7l-1.15 1q.05.325.05.65t-.05.65l1.15 1l-1 1.7l-1.45-.45q-.275.2-.537.338t-.563.262l-.3 1.5zm1-3q.825 0 1.413-.587T8.85 7t-.587-1.412T6.85 5t-1.412.588T4.85 7t.588 1.413T6.85 9m7.95 14l-.45-2.1q-.425-.15-.787-.363t-.713-.487l-2 .65l-1.4-2.4l1.6-1.4Q11 16.45 11 16t.05-.9l-1.6-1.4l1.4-2.4l2 .65q.35-.275.713-.488t.787-.362L14.8 9h2.8l.45 2.1q.425.15.788.363t.712.487l2-.65l1.4 2.4l-1.6 1.4q.05.45.05.9t-.05.9l1.6 1.4l-1.4 2.4l-2-.65q-.35.275-.712.487t-.788.363L17.6 23zm1.4-4q1.25 0 2.125-.875T19.2 16t-.875-2.125T16.2 13t-2.125.875T13.2 16t.875 2.125T16.2 19"
			/></svg
		>

		Generate Images
	</button>
</div>
