<script lang="ts">
	import { classList } from "$lib/classList";
    import OptionSelector from "$lib/imageConfiguration/OptionSelector.svelte";
	import LoadingModal from "$lib/LoadingModal.svelte";
	import { loadingState } from "$lib/loadingState.svelte";
    import MenuViewer from "$lib/preview/MenuViewer.svelte";
    import TextPreview from "$lib/preview/TextPreview.svelte";
    import { onMount } from "svelte";
    import { menuState, saveMenuToLocalStorage, clearRegenerationFlag } from "$lib/menuState.svelte";
    import { getNextWeekText, buildCells, generateEmailText } from "$lib/menuRenderer";
    import type { MenuStyleConfig, Ingredient } from "$lib/menuRenderer/types";

    let customOpen = $state(true);

    let customClass = $derived(customOpen ? "p-3 h-full" : "h-8 p-0 overflow-hidden xl:overflow-auto")

    let mailText = $state("");
    let styleConfig = $state<MenuStyleConfig | null>(null);
    let ingredients = $state<Ingredient[]>([]);

    // Derived states for menu rendering
    let weekText = $derived(getNextWeekText());
    let horizontalWeekText = $derived(weekText.split('\n').join(' '));
    
    let verticalCells = $derived(
        styleConfig ? buildCells(
            'vertical',
            menuState.data.header,
            menuState.data.content,
            styleConfig.layouts.vertical.grid.rows,
            styleConfig.layouts.vertical.grid.cols
        ) : []
    );

    let horizontalCells = $derived(
        styleConfig ? buildCells(
            'horizontal',
            menuState.data.header,
            menuState.data.content,
            styleConfig.layouts.horizontal.grid.rows,
            styleConfig.layouts.horizontal.grid.cols
        ) : []
    );

    onMount(async () => {
        // Load static data
        const [styleRes, ingredientsRes] = await Promise.all([
            fetch('/style.json'),
            fetch('/ingredients.json')
        ]);
        
        styleConfig = await styleRes.json();
        ingredients = await ingredientsRes.json();

        // Generate initial email text
        updateEmailText();
    });

    function updateEmailText() {
        if (ingredients.length > 0) {
            mailText = generateEmailText(
                menuState.data.content,
                ingredients,
                menuState.data['text-custom-french'],
                menuState.data['text-custom-english']
            );
        }
    }

    function generateImage() {
        customOpen = !customOpen;
    }

    function handleMenuGenerated() {
        updateEmailText();
        saveMenuToLocalStorage();
        clearRegenerationFlag();
        loadingState.loading = false;
    }
</script>





<main class="flex h-full flex-1 gap-3 justify-evenly overflow-hidden flex-col xl:flex-row">
    <OptionSelector 
        class="transition-all xl:p-3 xl:h-auto xl:max-h-full overflow-auto [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-linear-to-bl [&::-webkit-scrollbar-thumb]:from-amber-700 [&::-webkit-scrollbar-thumb]:to-orange-600 [&::-webkit-scrollbar-thumb]:rounded-full {customClass}"
        onclick={() => generateImage()}
        imageGeneratedCallback={handleMenuGenerated}
    >
        <div class="w-full xl:hidden">
            <button class="w-full cursor-pointer hover:underline" onclick="{() => customOpen = !customOpen}">
                {customOpen ? "Close for less surprise" : "Open for a surprise"}
            </button>
        </div>
    </OptionSelector>

    <div class="flex gap-3 lg:max-h-full rounded-lg flex-1 md:flex-row flex-col w-full overflow-auto [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-linear-to-bl [&::-webkit-scrollbar-thumb]:from-amber-700 [&::-webkit-scrollbar-thumb]:to-orange-600 [&::-webkit-scrollbar-thumb]:rounded-full">
        
        {#if styleConfig}
            <MenuViewer
                name="vertical"
                layoutName="vertical"
                layout={styleConfig.layouts.vertical}
                colors={styleConfig.colors}
                weekText={weekText}
                cells={verticalCells}
                logoPath="/Barbare.png"
                aspectRatio="aspect-1080/1920"
                skeleton={loadingState.loading}
            />
        {/if}
        
        <div class="flex flex-1 flex-col gap-3 md:overflow-auto [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar]:h-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-linear-to-bl [&::-webkit-scrollbar-thumb]:from-amber-700 [&::-webkit-scrollbar-thumb]:to-orange-600 [&::-webkit-scrollbar-thumb]:rounded-full">

            {#if styleConfig}
                <MenuViewer
                    name="horizontal"
                    layoutName="horizontal"
                    layout={styleConfig.layouts.horizontal}
                    colors={styleConfig.colors}
                    weekText={horizontalWeekText}
                    cells={horizontalCells}
                    logoPath="/Barbare.png"
                    skeleton={loadingState.loading}
                />
            {/if}

            <TextPreview class="overflow-auto max-h-full [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-linear-to-bl [&::-webkit-scrollbar-thumb]:from-amber-700 [&::-webkit-scrollbar-thumb]:to-orange-600 [&::-webkit-scrollbar-thumb]:rounded-full" text={mailText} skeleton={loadingState.loading}/>
        </div>
    </div>

    <LoadingModal />
</main>

