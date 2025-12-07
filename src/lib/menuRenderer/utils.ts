import type { MenuCell, MenuItem, Ingredient, MealOption } from './types';

/**
 * Get the next week text in French format (next Monday to Friday)
 */
export function getNextWeekText(): string {
	const today = new Date();
	const daysAhead = 7 - ((today.getDay() + 6) % 7); // Days until next Monday
	const monday = new Date(today);
	monday.setDate(today.getDate() + daysAhead);
	
	const friday = new Date(monday);
	friday.setDate(monday.getDate() + 4);

	const months = [
		'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
		'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
	];

	const mondayDay = monday.getDate().toString().padStart(2, '0');
	const fridayDay = friday.getDate().toString().padStart(2, '0');
	const month = months[friday.getMonth()];
	const year = friday.getFullYear();

	return `SEMAINE DU ${mondayDay} AU ${fridayDay} ${month.toUpperCase()}\n${year}`;
}

/**
 * Build cells for a specific layout
 */
export function buildCells(
	layoutName: 'vertical' | 'horizontal',
	headers: string[],
	content: Array<{ day: string; content: MenuItem[] }>,
	rows: number,
	cols: number
): MenuCell[] {
	const maxCells = rows * cols;
	const cells: MenuCell[] = [];

	for (let index = 0; index < maxCells; index++) {
		const headerLabel = headers[index] || '';
		const dayEntry = content[index];

		let label = headerLabel;
		if (!label && dayEntry) {
			label = dayEntry.day || `Jour ${index + 1}`;
		} else if (!label) {
			label = `Jour ${index + 1}`;
		}

		const items = dayEntry ? dayEntry.content : [];

		cells.push({ label, items });
	}

	return cells;
}

/**
 * Transform PascalCase to space-separated words
 */
export function transformPascalCase(text: string): string {
	if (text === 'RSAv') {
		return text;
	}

	const result: string[] = [''];
	for (let i = 0; i < text.length; i++) {
		if (text[i] === text[i].toUpperCase() && i !== 0) {
			result.push('');
		}
		result[result.length - 1] += text[i];
	}

	return result.map((word) => word.trim()).join(' ');
}

/**
 * Find ingredient information in the ingredients list
 */
export function findIngredient(ingredients: Ingredient[], name: string): Ingredient {
	if (name.toLowerCase() === 'pizza') {
		return ['Pizza', 'Pizza', 'Pizza'];
	}

	const normalizedName = name
		.toLowerCase()
		.normalize('NFD')
		.replace(/[\u0300-\u036f]/g, '');

	for (const ingredient of ingredients) {
		const normalizedIngredient = ingredient[0]
			.toLowerCase()
			.normalize('NFD')
			.replace(/[\u0300-\u036f]/g, '');

		if (normalizedIngredient.includes(normalizedName)) {
			return ingredient;
		}
	}

	console.warn(`Ingredient not found: ${name}`);
	return [`Not found: ${name}`, '', ''];
}

/**
 * Flatten meals and remove duplicates
 */
export function flattenMeals(content: Array<{ day: string; content: MenuItem[] }>): MenuItem[] {
	const allMeals: MenuItem[] = [];
	for (const day of content) {
		for (const item of day.content) {
			allMeals.push(item);
		}
	}

	// Remove duplicates based on text field
	const uniqueMeals: MenuItem[] = [];
	const seenTexts = new Set<string>();
	for (const meal of allMeals) {
		if (!seenTexts.has(meal.text)) {
			uniqueMeals.push(meal);
			seenTexts.add(meal.text);
		}
	}

	return uniqueMeals;
}

/**
 * Generate email text with ingredient information
 */
export function generateEmailText(
	content: Array<{ day: string; content: MenuItem[] }>,
	ingredients: Ingredient[],
	customTextFrench: string,
	customTextEnglish: string
): string {
	const uniqueMeals = flattenMeals(content);

	let text =
		'👇English translation under the picture, at the end of the email👇\nBonjour à tous !\n{text-custom-french}\n\nVoici la liste des ingrédients des plats:\n';

	// Add French ingredients
	for (const meal of uniqueMeals) {
		if (meal.is_meal) {
			const ingredient = findIngredient(ingredients, meal.text);
			if (ingredient[0] === 'Pizza') {
				continue;
			}
			text += `\t- ${ingredient[0]}: ${ingredient[1]}\n`;
		}
	}

	// Add English translation
	text +=
		'\n\n\n\n\n\n{image goes here}\n\n\n\n\n\n👇English translation👇\n\nHello everyone!\n{text-custom-english}\n\nHere is the list of ingredients of the dishes:\n';

	// Add English ingredients
	for (const meal of uniqueMeals) {
		if (meal.is_meal) {
			const ingredient = findIngredient(ingredients, meal.text);
			if (ingredient[0] === 'Pizza') {
				continue;
			}
			text += `\t- ${ingredient[0]}: ${ingredient[2]}\n`;
		}
	}

	text += "\n\nBar'barement vôtre,\nL'équipe Bar'bare";

	// Replace placeholders with custom text
	return text
		.replace('{text-custom-french}', customTextFrench)
		.replace('{text-custom-english}', customTextEnglish);
}

/**
 * Get meal text from meal list
 */
export function getMealText(mealList: MealOption[], mealImage: string): string {
	const meal = mealList.find((m) => m.image === mealImage);
	return meal?.name || '';
}
