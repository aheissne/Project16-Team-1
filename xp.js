
// xp.js — paste this on every page or link as
const XP_KEY = 'scafwording_xp';
const LEVEL_KEY = 'scafwording_level';
const XP_PER_LEVEL = 100; // change to 200 if you want slower leveling

function addXP(amount) {
    let xp = parseInt(localStorage.getItem(XP_KEY)) || 0;
    xp += amount;
    localStorage.setItem(XP_KEY, xp);

    // Level calculation
    let level = Math.floor(xp / XP_PER_LEVEL) + 1;
    localStorage.setItem(LEVEL_KEY, level);

    // Optional: celebrate level up
    const oldLevel = Math.floor((xp - amount) / XP_PER_LEVEL) + 1;
    if (level > oldLevel) {
        alert(`🎉 Level Up! You are now Level ${level}!`);
    }
}

function getXP() {
    return parseInt(localStorage.getItem(XP_KEY)) || 0;
}

function getLevel() {
    return parseInt(localStorage.getItem(LEVEL_KEY)) || 1;
}

function getXPForNextLevel() {
    const xp = getXP();
    return XP_PER_LEVEL - (xp % XP_PER_LEVEL);
}

// Show XP on any page easily
function renderXP(elementId = 'xpDisplay') {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = `Level ${getLevel()} • ${getXP()} XP (${getXPForNextLevel()} to next)`;
    }
}