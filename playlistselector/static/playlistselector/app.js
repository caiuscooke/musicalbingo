function handleDelete(playlistId, homepageUrl, csrf_token) {
  fetch(`/playlist/${playlistId}/`, {
    method: "DELETE",
    headers: {
      "X-CSRFToken": csrf_token,
      "Content-Type": "application/json",
    },
  }).then((response) => {
    if (response.ok) {
      window.alert("Playlist has been successfully removed.");
      window.location.href = homepageUrl;
    }
  });
}
