<script lang="ts">
    // Props
    export let uploadedImage: File | null = null;
    export let imagePreview = '';
    export let codeError = '';

    function handleImageUpload(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files[0]) {
            const file = input.files[0];
            uploadedImage = file;

            // Create preview
            const reader = new FileReader();
            reader.onload = (e) => {
                if (e.target) {
                    imagePreview = e.target.result as string;
                }
            };
            reader.readAsDataURL(file);
        }
    }
</script>

<div>
    <label for="imageUpload" class="block text-sm font-medium mb-1">Télécharger une image</label>
    <input
        id="imageUpload"
        type="file"
        accept="image/png,image/jpeg"
        on:change={handleImageUpload}
        class="block w-full text-sm text-white
            file:mr-4 file:py-2 file:px-4
            file:rounded file:border-0
            file:text-sm file:font-semibold
            file:bg-slate-800 file:text-white
            hover:file:bg-slate-700 cursor-pointer"
    />
    <p class="mt-1 text-gray-400 text-xs">L'image doit être au format PNG avec un fond transparent.</p>
    
    {#if imagePreview}
        <div class="mt-2 border rounded-lg p-2 bg-slate-700/20">
            <p class="text-sm mb-1">Aperçu:</p>
            <img src={imagePreview} alt="Preview" class="max-h-40 object-contain mx-auto" />
        </div>
    {/if}
</div>