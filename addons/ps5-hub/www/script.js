(function() {
  'use strict';

  var grid = document.getElementById('pluginGrid');
  var message = document.getElementById('message');
  var modal = document.getElementById('iframeModal');
  var iframeContainer = document.getElementById('iframeContainer');
  var modalClose = document.querySelector('.modal-close');
  var plugins = [];
  var focusedIndex = 0;

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function isValidTarget(target) {
    if (!target) return false;
    var lower = target.toLowerCase();
    return !lower.startsWith('javascript:') &&
           !lower.startsWith('data:') &&
           !lower.startsWith('vbscript:');
  }

  function createIconElement(plugin) {
    var img = document.createElement('img');
    img.src = plugin.icon || '';
    img.alt = plugin.name;
    img.className = 'plugin-icon';

    img.onerror = function() {
      var placeholder = document.createElement('div');
      placeholder.className = 'plugin-icon';
      placeholder.textContent = (plugin.name || '?')[0].toUpperCase();
      img.parentNode.replaceChild(placeholder, img);
    };

    return img;
  }

  function createPluginCard(plugin, index) {
    var card = document.createElement('a');
    card.href = '#';
    card.className = 'plugin-card';
    card.tabIndex = 0;

    card.appendChild(createIconElement(plugin));

    var name = document.createElement('div');
    name.className = 'plugin-name';
    name.textContent = plugin.name;
    card.appendChild(name);

    var desc = document.createElement('div');
    desc.className = 'plugin-description';
    desc.textContent = plugin.description || '';
    card.appendChild(desc);

    card.addEventListener('click', function(e) {
      e.preventDefault();
      handleCardClick(plugin);
    });

    card.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleCardClick(plugin);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        focusNearestCard(index, -1, 0);
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        focusNearestCard(index, 1, 0);
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        focusNearestCard(index, 0, -1);
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        focusNearestCard(index, 0, 1);
      }
    });

    return card;
  }

  function handleCardClick(plugin) {
    if (plugin.type === 'embed') {
      iframeContainer.src = plugin.target;
      modal.classList.remove('hidden');
      modalClose.focus();
    } else {
      window.location.href = plugin.target;
    }
  }

  function focusNearestCard(fromIndex, rowDelta, colDelta) {
    var cols = Math.max(1, Math.floor(grid.offsetWidth / 264));
    var newIndex = fromIndex + (rowDelta * cols) + colDelta;
    if (newIndex >= 0 && newIndex < plugins.length) {
      var cards = grid.querySelectorAll('.plugin-card');
      cards[newIndex].focus();
    }
  }

  function closeModal() {
    modal.classList.add('hidden');
    iframeContainer.src = '';
  }

  function loadPlugins() {
    fetch('plugins.json')
      .then(function(res) {
        if (!res.ok) throw new Error('Failed to load plugins');
        return res.json();
      })
      .then(function(data) {
        plugins = (data.plugins || []).filter(function(p) {
          return p.name && isValidTarget(p.target);
        });

        if (plugins.length === 0) {
          message.textContent = 'No plugins installed.';
          return;
        }

        grid.innerHTML = '';
        plugins.forEach(function(plugin, index) {
          grid.appendChild(createPluginCard(plugin, index));
        });

        var firstCard = grid.querySelector('.plugin-card');
        if (firstCard) firstCard.focus();
      })
      .catch(function(err) {
        console.error(err);
        message.textContent = 'Error loading plugins.';
      });
  }

  modalClose.addEventListener('click', closeModal);
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' || e.key === 'Backspace') {
      if (!modal.classList.contains('hidden')) {
        e.preventDefault();
        closeModal();
      }
    }
  });

  loadPlugins();
})();
