/* HTML Chat Archive Converter - Main JavaScript */

// Global variables
let conversationsData = [];
let filteredConversations = [];

// Initialize theme system
function initializeTheme() {
    const savedTheme = localStorage.getItem('chat-archive-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('chat-archive-theme', newTheme);
}

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const clearButton = document.getElementById('clear-search');
    
    if (!searchInput) return;
    
    // Load conversations data if available
    if (window.conversationsData) {
        conversationsData = window.conversationsData;
        filteredConversations = [...conversationsData];
    }
    
    searchInput.addEventListener('input', handleSearch);
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            clearSearch();
        }
    });
    
    if (clearButton) {
        clearButton.addEventListener('click', clearSearch);
    }
}

function handleSearch() {
    const searchInput = document.getElementById('search-input');
    const clearButton = document.getElementById('clear-search');
    const query = searchInput.value.toLowerCase().trim();
    
    // Show/hide clear button
    if (clearButton) {
        clearButton.style.display = query ? 'flex' : 'none';
    }
    
    // Filter conversations
    if (query) {
        filteredConversations = conversationsData.filter(conv => {
            return conv.title.toLowerCase().includes(query) ||
                   conv.preview?.toLowerCase().includes(query) ||
                   conv.source.toLowerCase().includes(query);
        });
    } else {
        filteredConversations = [...conversationsData];
    }
    
    // Apply other filters
    applyFilters();
    updateConversationsList();
}

function clearSearch() {
    const searchInput = document.getElementById('search-input');
    const clearButton = document.getElementById('clear-search');
    
    searchInput.value = '';
    if (clearButton) {
        clearButton.style.display = 'none';
    }
    
    filteredConversations = [...conversationsData];
    applyFilters();
    updateConversationsList();
    searchInput.focus();
}

// Initialize filters
function initializeFilters() {
    const sourceFilter = document.getElementById('source-filter');
    const sortFilter = document.getElementById('sort-filter');
    
    if (sourceFilter) {
        sourceFilter.addEventListener('change', applyFilters);
    }
    
    if (sortFilter) {
        sortFilter.addEventListener('change', applyFilters);
    }
}

function applyFilters() {
    const sourceFilter = document.getElementById('source-filter');
    const sortFilter = document.getElementById('sort-filter');
    
    let filtered = [...filteredConversations];
    
    // Apply source filter
    if (sourceFilter && sourceFilter.value) {
        filtered = filtered.filter(conv => conv.source === sourceFilter.value);
    }
    
    // Apply sorting
    if (sortFilter && sortFilter.value) {
        const sortBy = sortFilter.value;
        
        filtered.sort((a, b) => {
            switch (sortBy) {
                case 'date-desc':
                    return new Date(b.created_at || 0) - new Date(a.created_at || 0);
                case 'date-asc':
                    return new Date(a.created_at || 0) - new Date(b.created_at || 0);
                case 'title-asc':
                    return a.title.localeCompare(b.title);
                case 'title-desc':
                    return b.title.localeCompare(a.title);
                case 'messages-desc':
                    return (b.message_count || 0) - (a.message_count || 0);
                case 'messages-asc':
                    return (a.message_count || 0) - (b.message_count || 0);
                default:
                    return 0;
            }
        });
    }
    
    filteredConversations = filtered;
}

function updateConversationsList() {
    const conversationsList = document.getElementById('conversations-list');
    const noResults = document.getElementById('no-results');
    
    if (!conversationsList) return;
    
    // Hide all current items
    const items = conversationsList.querySelectorAll('.conversation-item');
    items.forEach(item => item.style.display = 'none');
    
    if (filteredConversations.length === 0) {
        if (noResults) {
            noResults.style.display = 'block';
        }
        return;
    }
    
    if (noResults) {
        noResults.style.display = 'none';
    }
    
    // Show matching items
    filteredConversations.forEach(conv => {
        const item = conversationsList.querySelector(`[data-title*="${conv.title.toLowerCase()}"]`);
        if (item) {
            item.style.display = 'block';
        }
    });
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else if (diffDays < 30) {
        const weeks = Math.floor(diffDays / 7);
        return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
}

function highlightSearchTerms(text, query) {
    if (!query) return text;
    
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

// Copy functionality for conversation pages
function copyMessage(button) {
    const messageText = button.parentElement.querySelector('.message-text').textContent;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(messageText).then(() => {
            showCopyFeedback(button);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            fallbackCopyTextToClipboard(messageText, button);
        });
    } else {
        fallbackCopyTextToClipboard(messageText, button);
    }
}

function fallbackCopyTextToClipboard(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopyFeedback(button);
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }
    
    document.body.removeChild(textArea);
}

function showCopyFeedback(button) {
    const originalHTML = button.innerHTML;
    button.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20,6 9,17 4,12"></polyline>
        </svg>
    `;
    
    setTimeout(() => {
        button.innerHTML = originalHTML;
    }, 1000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search focus
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    // Ctrl/Cmd + D for theme toggle
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        toggleTheme();
    }
});

// Smooth scrolling for anchor links
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && e.target.getAttribute('href').startsWith('#')) {
        e.preventDefault();
        const targetId = e.target.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Auto-resize search input on mobile
function handleMobileSearch() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;
    
    if (window.innerWidth <= 768) {
        searchInput.addEventListener('focus', function() {
            setTimeout(() => {
                window.scrollTo(0, 0);
            }, 300);
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    initializeSearch();
    initializeFilters();
    handleMobileSearch();
    
    // Add loading state management
    document.body.classList.add('loaded');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // Refresh theme in case it was changed in another tab
        const savedTheme = localStorage.getItem('chat-archive-theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    }
});

// Export functions for global access
window.initializeTheme = initializeTheme;
window.initializeSearch = initializeSearch;
window.initializeFilters = initializeFilters;
window.copyMessage = copyMessage;