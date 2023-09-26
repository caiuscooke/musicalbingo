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

function dropdownMenu() {
  console.log("dropdownMenu function began executing");

  const trigger = document.getElementById("dropdown-trigger");
  const menu = document.getElementById("dropdown-menu");

  trigger.addEventListener("click", function (event) {
    event.preventDefault();
    menu.classList.toggle("hidden");
  });

  // Close the dropdown when clicking outside of it
  document.addEventListener("click", function (event) {
    if (!menu.contains(event.target) && !trigger.contains(event.target)) {
      menu.classList.add("hidden");
    }
  });
}

document.addEventListener("DOMContentLoaded", dropdownMenu);
