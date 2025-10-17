<script lang="ts">
	import WeekIndication from './WeekIndication.svelte';
	import DayOption from './DayOption.svelte';
	import CommandPalette from '$lib/CommandPalette.svelte';
	import type { DayOptions } from '../type';
	import { imgLinkState, loadingState } from '$lib/loadingState.svelte';
	import { buildApiUrl } from '$lib/api';
	import { onMount } from 'svelte';

	const {
		class: class_ = '',
		children,
		onclick = () => {},
		imageGeneratedCallback = () => {}
	} = $props();

	let contentDiv = $state<HTMLElement | null>(null);
	let weekOption: { label: string; space: DayOptions[] }[] = $state([]);
	let commandPaletteOpen = $state(false);

	/**
	 * Sets up the week options based on the provided data.
	 * @param data - The data containing header and content for each day.
	 */
	function setupWeekOption(data: { header: string[]; content: any[] }) {
		weekOption = data['header'].map((day: string, index: number) => {
			let space: any[] = data['content'][index]['content'].map((space: any) => {
				return {
					is_used: true,
					is_meal: space['is_meal'],
					text: space['text'],
					meal: space['img'] || undefined
				};
			});

			space = space.concat(
				Array(2 - space.length)
					.fill(0)
					.map(() => {
						return {
							is_used: false,
							is_meal: true,
							text: '',
							meal: undefined
						};
					})
			);

			return {
				label: day,
				space: space
			};
		});
	}

	const customTextFrench = 'Voici le menu de cette semaine !';
	const customTextEnglish = 'Here is the menu for this week!';
	const dayAlias: Record<string, string> = {
		mon: 'lundi',
		monday: 'lundi',
		tue: 'mardi',
		tuesday: 'mardi',
		wed: 'mercredi',
		wednesday: 'mercredi',
		thu: 'jeudi',
		thur: 'jeudi',
		thurs: 'jeudi',
		thursday: 'jeudi',
		fri: 'vendredi',
		friday: 'vendredi',
		sat: 'samedi',
		saturday: 'samedi',
		sun: 'dimanche',
		sunday: 'dimanche',
		pub: 'pub'
	};

	let mealList: {
		name: string;
		image: string;
	}[] = $state([]);

	onMount(() => {
		const keyboardHandler = (event: KeyboardEvent) => {
			if ((event.ctrlKey || event.metaKey) && (event.key === 'k' || event.key === 'K')) {
				event.preventDefault();
				commandPaletteOpen = true;
			}
		};

		window.addEventListener('keydown', keyboardHandler);

		fetch(buildApiUrl('/getMealList'), {
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

		fetch(buildApiUrl('/getLastMenu'), {
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

		return () => {
			window.removeEventListener('keydown', keyboardHandler);
		};
	});

	function getMealText(meal: string) {
		return mealList.find((mealOption: any) => mealOption.image === meal)?.name || '';
	}

	function resolveDayLabel(token: string) {
		const normalized = token.toLowerCase();
		const exact = weekOption.find((day) => day.label.toLowerCase() === normalized);
		if (exact) {
			return exact.label;
		}

		const alias = dayAlias[normalized];
		if (alias) {
			const aliasMatch = weekOption.find((day) => day.label.toLowerCase() === alias);
			if (aliasMatch) {
				return aliasMatch.label;
			}
		}

		return null;
	}

	function getAvailableAliasTokens() {
		const availableLabels = weekOption.map((day) => day.label.toLowerCase());
		const matchedTokens = new Map<string, string>();

		Object.entries(dayAlias).forEach(([token, label]) => {
			if (availableLabels.includes(label)) {
				matchedTokens.set(token, label);
			}
		});

		const preferredOrder = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'pub'];
		const orderedTokens: string[] = [];

		preferredOrder.forEach((token) => {
			if (matchedTokens.has(token)) {
				orderedTokens.push(token);
				matchedTokens.delete(token);
			}
		});

		matchedTokens.forEach((_label, token) => {
			orderedTokens.push(token);
		});

		if (!orderedTokens.length) {
			availableLabels.forEach((label) => {
				if (!orderedTokens.includes(label)) {
					orderedTokens.push(label);
				}
			});
		}

		return orderedTokens;
	}

	function buildCommandCombos() {
		const tokens = getAvailableAliasTokens();
		const combos: { combo: string; requiresValue: boolean }[] = [];

		tokens.forEach((token) => {
			if (token.length > 4) {
				return;
			}

			['u', 'l'].forEach((zone) => {
				combos.push({ combo: `${token}-${zone}-s`, requiresValue: true });
				combos.push({ combo: `${token}-${zone}-t`, requiresValue: true });
				combos.push({ combo: `${token}-${zone}-clear`, requiresValue: false });
			});
		});

		if (!combos.length) {
			weekOption.forEach((day) => {
				['u', 'l'].forEach((zone) => {
					combos.push({ combo: `${day.label}-${zone}-s`, requiresValue: true });
					combos.push({ combo: `${day.label}-${zone}-t`, requiresValue: true });
					combos.push({ combo: `${day.label}-${zone}-clear`, requiresValue: false });
				});
			});
		}

		return combos;
	}

	function commandPaletteSuggestions(input: string) {
		const trimmedInput = input.replace(/\s+/g, ' ').trimStart();
		const combos = buildCommandCombos();

		if (!trimmedInput.length) {
			const baseToken = combos[0]?.combo.split('-')[0] || 'mon';
			return [
				'generate',
				`${baseToken}-u-s <sandwich name>`,
				`${baseToken}-u-t <your text>`,
				`${baseToken}-u-clear`
			];
		}

		const normalized = trimmedInput.toLowerCase();
		const hasSpace = trimmedInput.includes(' ');
		const suggestions: string[] = [];

		if (!hasSpace) {
			['generate', 'gen'].forEach((token) => {
				if (token.startsWith(normalized)) {
					suggestions.push(token);
				}
			});

			combos.forEach(({ combo, requiresValue }) => {
				if (combo.startsWith(normalized)) {
					suggestions.push(requiresValue ? `${combo} ` : combo);
				}
			});

			return suggestions.slice(0, 6);
		}

		const [head, ...restParts] = trimmedInput.split(/\s+/);
		const rest = restParts.join(' ');
		const lowerHead = head.toLowerCase();
		const [, , typeSegment = ''] = lowerHead.split('-');

		if (['generate', 'gen'].some((token) => token.startsWith(lowerHead))) {
			return ['generate'];
		}

		if (!head.includes('-')) {
			combos.forEach(({ combo, requiresValue }) => {
				if (combo.startsWith(lowerHead)) {
					suggestions.push(requiresValue ? `${combo} ` : combo);
				}
			});
			return suggestions.slice(0, 6);
		}

		if (!typeSegment.length) {
			return [];
		}

		if (typeSegment === 's') {
			const search = rest.toLowerCase();
			const matches = mealList
				.filter((meal) => !search || meal.name.toLowerCase().includes(search))
				.slice(0, 6)
				.map((meal) => `${head} ${meal.name}`);

			if (matches.length) {
				return matches;
			}

			if (!rest.length) {
				return mealList.slice(0, 6).map((meal) => `${head} ${meal.name}`);
			}
		}

		if (typeSegment === 't' && !rest.length) {
			return [`${head} <your text>`];
		}

		if (['clear', 'empty', 'reset'].includes(typeSegment)) {
			return [head];
		}

		return [];
	}

	function executeCommand(command: string) {
		if (!weekOption.length) {
			return {
				success: false,
				message: 'Menu data is still loading. Please try again in a moment.'
			};
		}

		const trimmed = command.trim();
		const normalizedCommand = trimmed.toLowerCase();

		if (normalizedCommand === 'generate' || normalizedCommand === 'gen') {
			if (loadingState.loading) {
				return {
					success: false,
					message: 'Generation is already in progress.'
				};
			}

			startGeneration();
			return {
				success: true,
				message: 'Started image generation.'
			};
		}

		const clearMatch = trimmed.match(/^([a-zA-Z]+)-(u|l)-(clear|empty|reset)$/i);
		if (clearMatch) {
			const [, dayToken, zoneToken] = clearMatch;
			const dayLabel = resolveDayLabel(dayToken);
			if (!dayLabel) {
				return {
					success: false,
					message: `Unknown day "${dayToken}". Please check the day name.`
				};
			}

			const dayIndex = weekOption.findIndex(
				(day) => day.label.toLowerCase() === dayLabel.toLowerCase()
			);
			if (dayIndex === -1) {
				return {
					success: false,
					message: `Day "${dayLabel}" is not available.`
				};
			}

			const zoneIndex = zoneToken.toLowerCase() === 'u' ? 0 : 1;
			const day = weekOption[dayIndex];
			const targetSpace = day.space[zoneIndex];
			if (!targetSpace) {
				return {
					success: false,
					message: `The ${zoneIndex === 0 ? 'upper' : 'lower'} zone is not available for ${day.label}.`
				};
			}

			targetSpace.is_used = false;
			targetSpace.is_meal = true;
			targetSpace.text = '';
			targetSpace.meal = undefined;

			if (zoneIndex === 0 && day.space[1]) {
				day.space[1].is_used = false;
				day.space[1].is_meal = true;
				day.space[1].text = '';
				day.space[1].meal = undefined;
			}
			weekOption = [...weekOption];

			return {
				success: true,
				message: `Cleared the ${zoneIndex === 0 ? 'upper' : 'lower'} zone for ${day.label}.`
			};
		}

		const match = trimmed.match(/^([a-zA-Z]+)-(u|l)-(s|t)\s+(.+)$/);
		if (!match) {
			return {
				success: false,
				message: 'Invalid command. Use day-zone-type value or day-zone-clear.'
			};
		}

		const [, dayToken, zoneToken, typeToken, payload] = match;
		const dayLabel = resolveDayLabel(dayToken);
		if (!dayLabel) {
			return {
				success: false,
				message: `Unknown day "${dayToken}". Please check the day name.`
			};
		}

		const dayIndex = weekOption.findIndex(
			(day) => day.label.toLowerCase() === dayLabel.toLowerCase()
		);
		if (dayIndex === -1) {
			return {
				success: false,
				message: `Day "${dayLabel}" is not available.`
			};
		}

		const zoneIndex = zoneToken.toLowerCase() === 'u' ? 0 : 1;
		const value = payload.trim();
		if (!value) {
			return {
				success: false,
				message: 'Please provide a sandwich name or text to apply.'
			};
		}

		const day = weekOption[dayIndex];
		const targetSpace = day.space[zoneIndex];
		if (!targetSpace) {
			return {
				success: false,
				message: `The ${zoneIndex === 0 ? 'upper' : 'lower'} zone is not available for ${day.label}.`
			};
		}

		if (zoneIndex === 1 && !day.space[0].is_used) {
			return {
				success: false,
				message: `Configure the upper zone for ${day.label} before using the lower zone.`
			};
		}

		targetSpace.is_used = true;

		const zoneLabel = zoneIndex === 0 ? 'upper' : 'lower';
		const type = typeToken.toLowerCase();

		if (type === 's') {
			if (!mealList.length) {
				return {
					success: false,
					message: 'Meal list is not available yet. Try again shortly.'
				};
			}

			const lowerValue = value.toLowerCase();
			let mealOption = mealList.find((meal) => meal.name.toLowerCase() === lowerValue);

			if (!mealOption) {
				const partialMatches = mealList.filter((meal) =>
					meal.name.toLowerCase().includes(lowerValue)
				);
				if (partialMatches.length === 1) {
					mealOption = partialMatches[0];
				} else if (partialMatches.length > 1) {
					return {
						success: false,
						message: `Multiple sandwiches match "${value}". Please be more specific.`
					};
				}
			}

			if (!mealOption) {
				return {
					success: false,
					message: `Sandwich "${value}" was not found in the meal list.`
				};
			}

			targetSpace.is_meal = true;
			targetSpace.text = '';
			targetSpace.meal = mealOption.image;
			weekOption = [...weekOption];
			return {
				success: true,
				message: `Set ${day.label} ${zoneLabel} zone to sandwich "${mealOption.name}".`
			};
		}

		targetSpace.is_meal = false;
		targetSpace.text = value;
		targetSpace.meal = undefined;
		weekOption = [...weekOption];
		return {
			success: true,
			message: `Updated ${day.label} ${zoneLabel} zone text.`
		};
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
	function startGeneration() {
		loadingState.loading = true;
		generateImage();
	}

	function generateImage() {
		let cli = weekOptionToCLI();
		fetch(buildApiUrl(`/generateImages?menu=${encodeURIComponent(cli)}`), {
			method: 'GET'
		}).then(async (data) => {
			if (data.ok) {
				const josn = await data.json();
				imgLinkState.horizontal = josn.horizontal;
				imgLinkState.vertical = josn.vertical;
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

	<div class="flex flex-wrap items-center justify-between gap-3">
		<div class="flex flex-wrap items-center gap-3">
			<h2 class="text-xl font-bold">Customization</h2>
		</div>

		<WeekIndication />
	</div>

	<button
		onclick={() => {
			commandPaletteOpen = true;
		}}
		class="rounded-md border mb-4 border-white/15 bg-white/10 px-3 py-1.5 text-xs font-medium tracking-wide text-white uppercase transition hover:bg-white/20 focus:ring-2 focus:ring-orange-400/60 focus:outline-none"
		type="button"
	>
		Command Palette (Ctrl+K)
	</button>

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
		onclick={startGeneration}
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

	<CommandPalette
		bind:isOpen={commandPaletteOpen}
		onCommand={executeCommand}
		getSuggestions={commandPaletteSuggestions}
	/>
</div>
