<script lang="ts">
	import TextSkeleton from "$lib/simpleComponent/TextSkeleton.svelte";

    const {
        class: classes = "",
        text,
        skeleton = false
    } = $props();

    let copied = $state(false);

    function copyToClipboard() {
        navigator.clipboard.writeText(text);
        copied = true;
        setTimeout(() => {
            copied = false;
        }, 2000);
    }
</script>

<div class="{classes} xl:overflow-hidden relative p-3 pt-4 bg-gray-600/20 rounded-lg bg-clip-padding backdrop-filter backdrop-blur-md border border-gray-100 flex-1">
    <h2 class="text-blue-gray-400 pointer-events-none absolute -top-1.5 translate-y-1.5 left-3 flex text-[11px] leading-tight font-normal transition-all select-none">
        Mail preview
    </h2>

    <div class="peer overflow-auto relative max-h-full [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar]:h-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-linear-to-bl [&::-webkit-scrollbar-thumb]:from-amber-700 [&::-webkit-scrollbar-thumb]:to-orange-600 [&::-webkit-scrollbar-thumb]:rounded-full">
        {#if !skeleton}
            <p class="whitespace-pre">
                {text}
            </p>
        {:else}
            <TextSkeleton />
        {/if}

    </div>
    <button class="flex gap-1 absolute bottom-3 left-1/2 -translate-x-1/2 bg-slate-900 p-1 px-2 rounded-lg hover:translate-y-0 hover:bg-slate-800 cursor-pointer translate-y-15 transition peer-hover:translate-y-0 active:bg-slate-500 active:border" onclick={copyToClipboard}>
        {#if copied}
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="m9.55 18l-5.7-5.7l1.425-1.425L9.55 15.15l9.175-9.175L20.15 7.4z" class="text-green-500"/></svg>
        {:else}
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M5 21q-.825 0-1.412-.587T3 19V5q0-.825.588-1.412T5 3h4.2q.325-.9 1.088-1.45T12 1t1.713.55T14.8 3H19q.825 0 1.413.588T21 5v14q0 .825-.587 1.413T19 21zm2-4h7v-2H7zm0-4h10v-2H7zm0-4h10V7H7zm5-4.75q.325 0 .538-.213t.212-.537t-.213-.537T12 2.75t-.537.213t-.213.537t.213.538t.537.212"/></svg>
        {/if}
        
        {copied ? "Copied" : "Copy to clipboard"}
    </button>
</div>