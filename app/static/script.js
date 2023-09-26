// base.html
document.addEventListener("DOMContentLoaded", () => {
  const $navbarBurgers = Array.prototype.slice.call(
    document.querySelectorAll(".navbar-burger"),
    0
  );

  $navbarBurgers.forEach((el) => {
    el.addEventListener("click", () => {
      const target = el.dataset.target;
      const $target = document.getElementById(target);
      el.classList.toggle("is-active");
      $target.classList.toggle("is-active");
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  (document.querySelectorAll(".notification .delete") || []).forEach(
    ($delete) => {
      const $notification = $delete.parentNode;

      $delete.addEventListener("click", () => {
        $notification.parentNode.removeChild($notification);
      });
    }
  );
});

// home.html
document.addEventListener("DOMContentLoaded", () => {
  (document.querySelectorAll(".card-header") || []).forEach(($cardHeader) => {
    const $cardContent = $cardHeader.nextElementSibling;

    const $icon =
      $cardHeader.firstElementChild.nextElementSibling.firstElementChild
        .firstElementChild;

    $cardHeader.addEventListener("click", () => {
      $cardContent.classList.toggle("is-hidden");
      $icon.classList.toggle("fa-rotate-180");
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  (document.querySelectorAll(".fa-heart") || []).forEach(($likeButton) => {
    const $postId = $likeButton.id.split("-")[2];

    const $numberOfLikes = document.getElementById(
      `number-of-likes-${$postId}`
    );

    $likeButton.addEventListener("click", async () => {
      const res = await fetch(`/like-post/${$postId}`, {
        method: "POST",
      }).catch((e) => {
        alert("エラーが発生しました");
      });
      const data = await res.json();
      $numberOfLikes.innerHTML = data["likes"];

      if (data["liked"] === true) {
        $likeButton.classList.replace("fa-regular", "fa-solid");
      } else {
        $likeButton.classList.replace("fa-solid", "fa-regular");
      }
    });
  });
});

// login.html, signup.html, delete.html

document.addEventListener("DOMContentLoaded", () => {
  (document.querySelectorAll(".fa-eye-slash") || []).forEach(($eyeIcon) => {
    const $passwordField =
      $eyeIcon.parentElement.parentElement.nextElementSibling.firstElementChild;

    $eyeIcon.addEventListener("click", () => {
      const $type = $passwordField.getAttribute("type") === "password";
      if ($type) {
        $passwordField.setAttribute("type", "text");
        $eyeIcon.className = "fa-solid fa-eye";
      } else {
        $passwordField.setAttribute("type", "password");
        $eyeIcon.className = "fa-regular fa-eye-slash";
      }
    });
  });
});
