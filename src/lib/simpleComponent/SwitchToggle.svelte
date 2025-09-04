<script>
	let { 
        checked = $bindable(false),
        label,
        key,
        class: classes = "",
    } = $props();

    const height = "h-3";
</script>

<div class="flex gap-1 {classes}">
	<div class="inline-flex items-center gap-2">
        <div class="relative inline-block w-11 {height}">
          <input id="{key}" bind:checked={checked} type="checkbox" class="peer appearance-none w-11 {height} absolute top-0 bg-slate-100 rounded-full checked:bg-slate-800 cursor-pointer transition-colors duration-300" />
          <label for="{key}" class="absolute top-0 left-0 w-5 {height} bg-white rounded-full border border-slate-300 shadow-sm transition-transform duration-300 peer-checked:translate-x-6 peer-checked:border-slate-800 cursor-pointer">
          </label>
        </div>
        <label for="{key}" class="text-white text-sm cursor-pointer">{label}</label>
       
      </div>
</div>
