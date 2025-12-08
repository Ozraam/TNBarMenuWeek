import { type MenuItem } from './menuRenderer/types';

export type DayContent = {
	day: string;
	content: MenuItem[];
};

export type MenuData = {
	header: string[];
	content: DayContent[];
	'text-custom-french': string;
	'text-custom-english': string;
};

// Store for menu state
export const menuState = $state<{
	data: MenuData;
	needsRegeneration: boolean;
}>({
	data: {
		header: ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'pub'],
		content: [],
		'text-custom-french': 'Voici le menu de cette semaine !',
		'text-custom-english': 'Here is the menu for this week!'
	},
	needsRegeneration: true
});

// Initialize default content
menuState.data.content = menuState.data.header.map((day) => ({
	day,
	content: []
}));

// Load saved menu data from localStorage if available
if (typeof window !== 'undefined') {
	const savedMenu = localStorage.getItem('lastMenu');
	if (savedMenu) {
		try {
			const parsed = JSON.parse(savedMenu);
			menuState.data = parsed;
			menuState.needsRegeneration = false;
		} catch (e) {
			console.error('Failed to load saved menu:', e);
		}
	}
}

export function saveMenuToLocalStorage() {
	if (typeof window !== 'undefined') {
		localStorage.setItem('lastMenu', JSON.stringify(menuState.data));
	}
}

export function markForRegeneration() {
	menuState.needsRegeneration = true;
}

export function clearRegenerationFlag() {
	menuState.needsRegeneration = false;
}
