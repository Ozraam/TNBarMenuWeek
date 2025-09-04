<script lang="ts">

    let {
        key = "select",
        label,
        options,
        selected = $bindable(),
		class: classes = "w-full",
    } : {
        key: string;
        label: string;
        options: {
            value: string;
            label: string;
        }[];
        selected: string | undefined;
		class: string;
    } = $props();

	let selectedValue = $state();
</script>

<div class="w-full min-w-[200px] {classes}">
	<label class="mb-1 block text-sm" for="{key}"> {label} </label>

	<div class="relative">
		<select
            id="{key}"
            bind:value={selected}
			class="ease w-full cursor-pointer appearance-none rounded border border-slate-200 bg-transparent py-2 pr-8 pl-3 text-sm shadow-sm transition duration-300 placeholder:text-slate-400 hover:border-slate-400 focus:border-slate-400 focus:shadow-md focus:outline-none"
		>
			{#each options as { value, label }}
                <option class="text-slate-700" {value}>{label}</option>
            {/each}
		</select>
		<svg
			xmlns="http://www.w3.org/2000/svg"
			fill="none"
			viewBox="0 0 24 24"
			stroke-width="1.2"
			stroke="currentColor"
			class="absolute top-2.5 right-2.5 ml-1 h-5 w-5 text-white"
		>
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				d="M8.25 15 12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9"
			/>
		</svg>
	</div>

	{selectedValue}
</div>
