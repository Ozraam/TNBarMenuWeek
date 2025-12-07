<script lang="ts">
	import { classList } from '$lib/classList';
	import { onMount } from 'svelte';
	import type { MealOption, Ingredient } from '$lib/menuRenderer/types';
	
	// Import our new components
	import SandwichBasicInfo from '$lib/sandwichForm/SandwichBasicInfo.svelte';
	import SandwichImageUpload from '$lib/sandwichForm/SandwichImageUpload.svelte';
	import SandwichDescription from '$lib/sandwichForm/SandwichDescription.svelte';
	import FormMessage from '$lib/sandwichForm/FormMessage.svelte';

	// Form state
	let sandwichName = $state('');
	let imageCode = $state('');
	let frenchDescription = $state('');
	let englishDescription = $state('');
	let isVegetarian = $state(false);
	let uploadedImage = $state<File | null>(null);
	let existingMeals = $state<MealOption[]>([]);
	let existingIngredients = $state<Ingredient[]>([]);
	let isSubmitting = $state(false);
	let formMessage = $state({ text: '', type: '' });

	// Upload preview
	let imagePreview = $state('');

	// Validation state
	let nameError = $state('');
	let codeError = $state('');
	let descriptionError = $state('');

	onMount(async () => {
		await loadExistingData();
	});

	async function loadExistingData() {
		try {
			// Load meal list from static file
			const mealsResponse = await fetch('/mealList.json');
			const staticMeals: MealOption[] = await mealsResponse.json();
			
			// Load from localStorage (custom added meals)
			const customMeals = localStorage.getItem('customMeals');
			const customMealsList: MealOption[] = customMeals ? JSON.parse(customMeals) : [];
			
			existingMeals = [...staticMeals, ...customMealsList];

			// Load ingredients
			const ingredientsResponse = await fetch('/ingredients.json');
			const staticIngredients: Ingredient[] = await ingredientsResponse.json();
			
			const customIngredients = localStorage.getItem('customIngredients');
			const customIngredientsList: Ingredient[] = customIngredients ? JSON.parse(customIngredients) : [];
			
			existingIngredients = [...staticIngredients, ...customIngredientsList];
		} catch (error) {
			console.error('Failed to load existing data:', error);
		}
	}

	function validateForm(): boolean {
		let isValid = true;

		// Reset errors
		nameError = '';
		codeError = '';
		descriptionError = '';

		// Validate name
		if (!sandwichName.trim()) {
			nameError = 'Le nom du sandwich est requis';
			isValid = false;
		} else if (existingMeals.some(m => m.name.toLowerCase() === sandwichName.trim().toLowerCase())) {
			nameError = 'Ce nom de sandwich existe déjà';
			isValid = false;
		}

		// Validate image code
		if (!imageCode.trim() && !uploadedImage) {
			codeError = 'Un code d\'image ou un fichier est requis';
			isValid = false;
		} else if (imageCode.trim() && existingMeals.some(m => m.image.toLowerCase() === imageCode.trim().toLowerCase())) {
			codeError = 'Ce code d\'image est déjà utilisé';
			isValid = false;
		}

		// Validate descriptions
		if (!frenchDescription.trim()) {
			descriptionError = 'La description française est requise';
			isValid = false;
		}

		return isValid;
	}

	async function handleSubmit(e : Event) {
        e.preventDefault();
		if (!validateForm()) {
			return;
		}

		isSubmitting = true;
		formMessage = { text: '', type: '' };

		try {
			// Generate image code from name if not provided
			let finalImageCode = imageCode.trim() || sandwichName.trim().replace(/\s+/g, '');
			
			// Store uploaded image as data URL if provided
			if (uploadedImage) {
				const reader = new FileReader();
				reader.onload = async (e) => {
					const imageData = e.target?.result as string;
					const customImages = JSON.parse(localStorage.getItem('customImages') || '{}');
					customImages[finalImageCode] = imageData;
					localStorage.setItem('customImages', JSON.stringify(customImages));
				};
				reader.readAsDataURL(uploadedImage);
			}

			// Add to meal list
			const newMeal: MealOption = {
				name: sandwichName.trim(),
				image: finalImageCode
			};

			const customMeals = JSON.parse(localStorage.getItem('customMeals') || '[]');
			customMeals.push(newMeal);
			localStorage.setItem('customMeals', JSON.stringify(customMeals));

			// Add to ingredients
			let ingredientName = sandwichName.trim();
			if (isVegetarian && !ingredientName.toLowerCase().includes('végé') && !ingredientName.toLowerCase().includes('veggie')) {
				ingredientName = `${ingredientName} (végé/veggie)`;
			}

			const newIngredient: Ingredient = [
				ingredientName,
				frenchDescription.trim(),
				(englishDescription.trim() || frenchDescription.trim())
			];

			const customIngredients = JSON.parse(localStorage.getItem('customIngredients') || '[]');
			customIngredients.push(newIngredient);
			localStorage.setItem('customIngredients', JSON.stringify(customIngredients));

			formMessage = { 
				text: 'Sandwich ajouté avec succès! Vous pouvez maintenant l\'utiliser dans les menus.', 
				type: 'success' 
			};
			
			// Reset form
			sandwichName = '';
			imageCode = '';
			frenchDescription = '';
			englishDescription = '';
			isVegetarian = false;
			uploadedImage = null;
			imagePreview = '';
			
			// Refresh the list
			await loadExistingData();
		} catch (error) {
			console.error('Error submitting form:', error);
			formMessage = { 
				text: 'Une erreur est survenue lors de la création du sandwich.', 
				type: 'error' 
			};
		} finally {
			isSubmitting = false;
		}
	}
</script>

<main class="rounded-lg border flex-1 p-6 border-gray-100 bg-gray-600/20 bg-clip-padding backdrop-blur-md backdrop-filter">
	<h2 class="text-3xl font-bold mb-6">Ajouter un nouveau sandwich</h2>
	
	<div class="max-w-3xl mx-auto">
		<form onsubmit={handleSubmit} class="space-y-6">
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div class="space-y-4">
					<!-- Basic info component -->
					<SandwichBasicInfo 
						bind:sandwichName
						bind:imageCode
						bind:isVegetarian
						{nameError}
						{codeError}
					/>
					
					<!-- Image upload component -->
					<SandwichImageUpload 
						bind:uploadedImage
						bind:imagePreview
						{codeError}
					/>
				</div>

				<div>
					<!-- Description component -->
					<SandwichDescription 
						bind:frenchDescription
						bind:englishDescription
						{descriptionError}
					/>
				</div>
			</div>

			<!-- Submit button -->
			<div class="flex justify-center mt-6">
				<button
					type="submit"
					disabled={isSubmitting}
					class="flex items-center rounded-md border border-transparent bg-slate-800 px-6 py-3 text-center text-sm text-white shadow-sm transition-all hover:bg-slate-700 hover:shadow-lg focus:bg-slate-700 focus:shadow-none active:bg-slate-700 active:shadow-none disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none"
				>
					{#if isSubmitting}
						<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						Envoi en cours...
					{:else}
						<svg xmlns="http://www.w3.org/2000/svg" class="mr-1.5 h-5 w-5" viewBox="0 0 24 24">
							<path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6z"/>
						</svg>
						Ajouter le sandwich
					{/if}
				</button>
			</div>

			<!-- Form message -->
			<FormMessage message={formMessage} />
		</form>
	</div>

	<div class="mt-10">
		<h3 class="text-xl font-bold mb-3">Note importante</h3>
		<p class="text-gray-300">
			Cette interface vous permet d'ajouter de nouveaux sandwichs à la liste des options disponibles pour le menu.
			Une fois ajouté, le sandwich apparaîtra dans la liste des options lors de la création d'un menu.
		</p>
		<p class="mt-2 text-gray-300">
			L'image doit être au format PNG avec un fond transparent pour s'afficher correctement sur les images du menu.
		</p>
		<p class="mt-2 text-gray-300">
			Le code image doit être unique et sera utilisé pour référencer l'image dans le système.
		</p>
	</div>
</main>