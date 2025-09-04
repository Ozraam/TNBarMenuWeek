<script lang="ts">
    let {
        key = "textarea",
        label,
        value = $bindable(""),
    } : {
        key: string;
        label: string;
        value: string;
    } = $props();

</script>

<div class="w-96">
	<div class="relative w-full min-w-[200px]">
		<textarea
        id="{key}"
			class="peer border-blue-gray-200 not-placeholder-shown:border-t-transparent text-blue-gray-700 placeholder-shown:border-blue-gray-200 placeholder-shown:border-t-blue-gray-200 disabled:bg-blue-gray-50 h-full min-h-[100px] w-full resize-none rounded-[7px] border bg-transparent px-3 py-2.5 font-sans text-sm font-normal outline-0 transition-all placeholder-shown:border focus:border-2 focus:border-white focus:border-t-transparent focus:outline-0 disabled:resize-none disabled:border-0"
			placeholder=" "
            bind:value={value}
		></textarea>
		<label
			class="before:content[' '] after:content[' '] text-blue-gray-400 before:border-blue-gray-200 after:border-blue-gray-200 peer-placeholder-shown:text-blue-gray-500 peer-disabled:peer-placeholder-shown:text-blue-gray-500 pointer-events-none absolute -top-1.5 left-0 flex h-full w-full text-[11px] leading-tight font-normal transition-all select-none peer-placeholder-shown:text-sm peer-placeholder-shown:leading-[3.75] peer-focus:text-[11px] peer-focus:leading-tight peer-focus:text-white peer-disabled:text-transparent before:pointer-events-none before:mt-[6.5px] before:mr-1 before:box-border before:block before:h-1.5 before:w-2.5 before:rounded-tl-md before:border-t before:border-l before:transition-all peer-placeholder-shown:before:border-transparent peer-focus:before:border-t-2 peer-focus:before:border-l-2 peer-focus:before:border-white peer-disabled:before:border-transparent after:pointer-events-none after:mt-[6.5px] after:ml-1 after:box-border after:block after:h-1.5 after:w-2.5 after:flex-grow after:rounded-tr-md after:border-t after:border-r after:transition-all peer-placeholder-shown:after:border-transparent peer-focus:after:border-t-2 peer-focus:after:border-r-2 peer-focus:after:border-white peer-disabled:after:border-transparent"
            for="{key}"
        >
			{label}
		</label>
	</div>
</div>
