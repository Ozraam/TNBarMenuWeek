<script lang="ts">
    import Checkbox from '$lib/simpleComponent/Checkbox.svelte';
    
    // Props
    export let sandwichName = '';
    export let imageCode = '';
    export let isVegetarian = false;
    
    // Validation errors
    export let nameError = '';
    export let codeError = '';
</script>

<div class="space-y-4">
    <!-- Sandwich name -->
    <div>
        <label for="sandwichName" class="block text-sm font-medium mb-1">Nom du sandwich</label>
        <input 
            id="sandwichName"
            type="text"
            bind:value={sandwichName}
            class="ease w-full appearance-none rounded border border-slate-200 bg-transparent py-2 px-3 text-sm shadow-sm transition duration-300 placeholder:text-slate-400 hover:border-slate-400 focus:border-slate-400 focus:shadow-md focus:outline-none"
            placeholder="Le Nouveau"
        />
        {#if nameError}
            <p class="mt-1 text-red-400 text-sm">{nameError}</p>
        {/if}
    </div>

    <!-- Image code -->
    <div>
        <label for="imageCode" class="block text-sm font-medium mb-1">Code image (sans extension)</label>
        <input 
            id="imageCode"
            type="text"
            bind:value={imageCode}
            class="ease w-full appearance-none rounded border border-slate-200 bg-transparent py-2 px-3 text-sm shadow-sm transition duration-300 placeholder:text-slate-400 hover:border-slate-400 focus:border-slate-400 focus:shadow-md focus:outline-none"
            placeholder="Nouveau"
        />
        <p class="mt-1 text-gray-400 text-xs">Ce code sera utilisé pour nommer le fichier image.</p>
        {#if codeError}
            <p class="mt-1 text-red-400 text-sm">{codeError}</p>
        {/if}
    </div>

    <!-- Vegetarian checkbox -->
    <div class="mt-4">
        <Checkbox label="Sandwich végétarien" key="vegetarian" bind:checked={isVegetarian} />
    </div>
</div>