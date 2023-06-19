<script>
    function clearChat() {
        if (confirm('Apakah Anda yakin ingin menghapus semua chat?')) {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/clear-chat', true);
            xhr.onload = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    location.reload(); // Muat ulang halaman setelah chat dihapus
                }
            };
            xhr.send();
        }
    }
</script>
