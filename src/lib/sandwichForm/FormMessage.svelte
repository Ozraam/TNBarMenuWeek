<script lang="ts">
    export let message: { text: string; type: string } = { text: '', type: '' };
</script>

{#if message.text}
    <div class="mt-4 p-3 rounded-lg {message.type === 'success' ? 'bg-green-500/20 border border-green-500' : 'bg-red-500/20 border border-red-500'}">
        {message.text}
    </div>
{/if}