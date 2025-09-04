<script>
    const nextMonday = new Date();
    nextMonday.setDate(nextMonday.getDate() + (1 + 7 - nextMonday.getDay()) % 7);
    const nextFriday = new Date(nextMonday);
    nextFriday.setDate(nextFriday.getDate() + 4);
</script>

<p>
    Semaine du {nextMonday.toLocaleDateString('fr-FR', { day: 'numeric' })} au {nextFriday.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
</p>