<script lang="ts">
	import { classList } from '$lib/classList';
	import { onMount } from 'svelte';
	
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
	let existingNames = $state<string[]>([]);
	let isSubmitting = $state(false);
	let formMessage = $state({ text: '', type: '' });

	// Upload preview
	let imagePreview = $state('');

	// Validation state
	let nameError = $state('');
	let codeError = $state('');
	let descriptionError = $state('');

	onMount(() => {
		fetchExistingSandwiches();
	});

	async function fetchExistingSandwiches() {
		try {
			const response = await fetch('http://localhost:5000/getMealList');
			if (response.ok) {
				const mealList = await response.json();
				existingNames = mealList.map((meal: any) => meal.name);
			}
		} catch (error) {
			console.error('Failed to fetch existing sandwiches:', error);
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
		} else if (existingNames.includes(sandwichName.trim())) {
			nameError = 'Ce nom de sandwich existe déjà';
			isValid = false;
		}

		// Validate image code
		if (!imageCode.trim() && !uploadedImage) {
			codeError = 'Un code d\'image ou un fichier est requis';
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
			// Create formData
			const formData = new FormData();
			formData.append('name', sandwichName);
			formData.append('image', imageCode);
			formData.append('frenchDescription', frenchDescription);
			formData.append('englishDescription', englishDescription || frenchDescription);
			formData.append('isVegetarian', isVegetarian.toString());
			
			if (uploadedImage) {
				formData.append('imageFile', uploadedImage);
			}

			// This is a placeholder endpoint - actual implementation would depend on your backend
			const response = await fetch('http://localhost:5000/addSandwich', {
				method: 'POST',
				body: formData
			});

			if (response.ok) {
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
				
				// Refresh the list of existing sandwiches
				fetchExistingSandwiches();
			} else {
				const error = await response.json();
				formMessage = { text: error.message || 'Une erreur est survenue', type: 'error' };
			}
		} catch (error) {
			console.error('Error submitting form:', error);
			formMessage = { 
				text: 'Une erreur est survenue lors de la création du sandwich. Vérifiez que le serveur est en ligne.', 
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