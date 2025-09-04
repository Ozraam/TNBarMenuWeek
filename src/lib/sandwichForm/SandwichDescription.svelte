<script lang="ts">
    import Textarea from '$lib/simpleComponent/Textarea.svelte';
    
    // Props
    export let frenchDescription = '';
    export let englishDescription = '';
    export let descriptionError = '';
</script>

<div class="space-y-4">
    <!-- French description -->
    <div>
        <label for="frenchDesc" class="block text-sm font-medium mb-1">Description française</label>
        <Textarea 
            key="frenchDesc"
            label="Ingrédients en français" 
            bind:value={frenchDescription}
        />
        <p class="mt-1 text-gray-400 text-xs">Ex: jambon, fromage, tomates, salade.</p>
        {#if descriptionError}
            <p class="mt-1 text-red-400 text-sm">{descriptionError}</p>
        {/if}
    </div>

    <!-- English description -->
    <div>
        <label for="englishDesc" class="block text-sm font-medium mb-1">Description anglaise (facultatif)</label>
        <Textarea 
            key="englishDesc"
            label="Ingrédients en anglais" 
            bind:value={englishDescription}
        />
        <p class="mt-1 text-gray-400 text-xs">Ex: ham, cheese, tomatoes, salad.</p>
    </div>
</div>