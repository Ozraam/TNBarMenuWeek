<script lang="ts">
	import { classList } from "$lib/classList";
    import OptionSelector from "$lib/imageConfiguration/OptionSelector.svelte";
	import LoadingModal from "$lib/LoadingModal.svelte";
	import { imgLinkState, loadingState } from "$lib/loadingState.svelte";
    import ImageViewer from "$lib/preview/ImageViewer.svelte";
    import TextPreview from "$lib/preview/TextPreview.svelte";
	import { onMount } from "svelte";

    let customOpen = $state(true);

    let customClass = $derived(customOpen ? "p-3 h-full" : "h-8 p-0 overflow-hidden xl:overflow-auto")

    let mailText = $state("");

    let verticalImage : ImageViewer;
    let horizontalImage : ImageViewer;

    onMount(() => {
        getText();
    });

    function generateImage() {
        customOpen = !customOpen
    }

    function getText() {
        fetch("http://localhost:5000/getMailingText", {
            method: "GET",
        }).then((data) => {
                if (data.ok) {
                    data.json().then((text_api) => {
                        mailText = text_api.text;
                    });
                } else {
                    alert("An error occured");
                }
            }
        );
    }
</script>





<main class="flex h-full flex-1 gap-3 justify-evenly overflow-hidden flex-col xl:flex-row">
    <OptionSelector 
        class="transition-all xl:p-3 xl:h-auto xl:max-h-full overflow-auto [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-linear-to-bl [&::-webkit-scrollbar-thumb]:from-amber-700 [&::-webkit-scrollbar-thumb]:to-orange-600 [&::-webkit-scrollbar-thumb]:rounded-full {customClass}"
        onclick={() => generateImage()}
        imageGeneratedCallback={() => {
            getText();
            verticalImage?.getImage();
            horizontalImage?.getImage();
            loadingState.loading = false;
            
        }}
    >
        <div class="w-full xl:hidden">
            <button class="w-full cursor-pointer hover:underline" onclick="{() => customOpen = !customOpen}">
                {customOpen ? "Close for less surprise" : "Open for a surprise"}
            </button>
        </div>
    </OptionSelector>

    <div class="flex gap-3 lg:max-h-full rounded-lg flex-1 md:flex-row flex-col w-full overflow-auto [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-linear-to-bl [&::-webkit-scrollbar-thumb]:from-amber-700 [&::-webkit-scrollbar-thumb]:to-orange-600 [&::-webkit-scrollbar-thumb]:rounded-full">
        
            <ImageViewer name="vertical" bind:this={verticalImage} aspectRatio="aspect-1080/1920" skeleton={loadingState.loading} src="http://localhost:5000/verticalMenu?epoch={imgLinkState.vertical}" alt="un placeholder" />
        
        <div class="flex flex-1 flex-col gap-3 md:overflow-auto [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar]:h-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-linear-to-bl [&::-webkit-scrollbar-thumb]:from-amber-700 [&::-webkit-scrollbar-thumb]:to-orange-600 [&::-webkit-scrollbar-thumb]:rounded-full">

            <ImageViewer name="horizontal" bind:this={horizontalImage} src="http://localhost:5000/horizontalMenu?epoch={imgLinkState.horizontal}" alt="placeholder" skeleton={loadingState.loading}/>

            <TextPreview class="overflow-auto max-h-full [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-linear-to-bl [&::-webkit-scrollbar-thumb]:from-amber-700 [&::-webkit-scrollbar-thumb]:to-orange-600 [&::-webkit-scrollbar-thumb]:rounded-full" text={mailText} skeleton={loadingState.loading}/>
        </div>
    </div>

    <LoadingModal />
</main>

