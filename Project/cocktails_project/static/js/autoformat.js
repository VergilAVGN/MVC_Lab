const ingredients = document.getElementById('ingredients');
const steps = document.getElementById('instructions');

const formatIngredients = value => {
    return value
        .split(/\r?\n/)
        .map(line => line.trim())
        .filter(line => line.length)
        .map(line => line.replace(/^[\-\*\+]\s*/, ''))
        .map(line => '- ' + line)
        .join('\n');
};

const formatInstructions = value => {
    return value
        .split(/\r?\n/)
        .map(line => line.trim())
        .filter(line => line.length)
        .map((line, index) => {
            const cleaned = line.replace(/^\d+[\.\)]\s*/, '');
            return `${index + 1}. ${cleaned}`;
        })
        .join('\n');
};

const bindAutoformat = (element, formatFn) => {
    if (!element) return;

    let wasEmpty = element.value.trim() === '';

    const applyFormat = () => {
        const formatted = formatFn(element.value);
        if (formatted !== element.value) {
            element.value = formatted;
        }
    };

    const handleInput = () => {
        const currentValue = element.value.trim();
        if (wasEmpty && currentValue) {
            element.value = (element === ingredients ? '- ' : '1. ') + element.value;
            wasEmpty = false;
        } else if (!currentValue) {
            wasEmpty = true;
        }
    };

    const handleBackspace = (e) => {
        if (e.key !== 'Backspace') return;

        const start = element.selectionStart;
        const value = element.value;
        const lines = value.split(/\r?\n/);
        let lineIndex = 0;
        let charIndex = 0;

        for (let i = 0; i < lines.length; i++) {
            if (charIndex + lines[i].length >= start) {
                lineIndex = i;
                break;
            }
            charIndex += lines[i].length + 1; // +1 for \n
        }

        const currentLine = lines[lineIndex];
        const posInLine = start - charIndex;

        if (posInLine === 0 && currentLine.startsWith('- ')) {
            e.preventDefault();
            const beforeLine = lines.slice(0, lineIndex).join('\n');
            const afterLine = lines.slice(lineIndex + 1).join('\n');
            const newValue = beforeLine + (beforeLine ? '\n' : '') + afterLine;
            element.value = newValue;
            element.selectionStart = element.selectionEnd = beforeLine.length;
        } else if (posInLine === 2 && currentLine.startsWith('- ')) {
            e.preventDefault();
            const beforeLine = lines.slice(0, lineIndex).join('\n');
            const afterLine = lines.slice(lineIndex + 1).join('\n');
            const newValue = beforeLine + (beforeLine ? '\n' : '') + afterLine;
            element.value = newValue;
            element.selectionStart = element.selectionEnd = beforeLine.length;
        } else if (currentLine.match(/^\d+\.\s/)) {
            const match = currentLine.match(/^\d+\.\s/);
            if (posInLine === 0 || posInLine === match[0].length) {
                e.preventDefault();
                const beforeLine = lines.slice(0, lineIndex).join('\n');
                const afterLine = lines.slice(lineIndex + 1).join('\n');
                const newValue = beforeLine + (beforeLine ? '\n' : '') + afterLine;
                element.value = newValue;
                element.selectionStart = element.selectionEnd = beforeLine.length;
                applyFormat(); // переформатируем номера после удаления
            }
        }
    };

    const handleEnter = (e) => {
        if (e.key !== 'Enter') return;

        const start = element.selectionStart;
        const value = element.value;
        const lines = value.split(/\r?\n/);
        let lineIndex = 0;
        let charIndex = 0;

        for (let i = 0; i < lines.length; i++) {
            if (charIndex + lines[i].length >= start) {
                lineIndex = i;
                break;
            }
            charIndex += lines[i].length + 1;
        }

        const currentLine = lines[lineIndex];
        const posInLine = start - charIndex;

        if (element === ingredients && posInLine === currentLine.length) {
            e.preventDefault();
            const beforeCursor = value.substring(0, start);
            const afterCursor = value.substring(start);
            element.value = beforeCursor + '\n- ' + afterCursor;
            element.selectionStart = element.selectionEnd = start + 4; // after \n- 
        } else if (element === steps && posInLine === currentLine.length) {
            e.preventDefault();
            const nonEmptyLines = lines.filter(line => line.trim().length > 0);
            const nextNumber = nonEmptyLines.length + 1;
            const prefix = `\n${nextNumber}. `;
            const beforeCursor = value.substring(0, start);
            const afterCursor = value.substring(start);
            element.value = beforeCursor + prefix + afterCursor;
            element.selectionStart = element.selectionEnd = start + prefix.length;
        }
    };

    element.addEventListener('blur', applyFormat);
    element.addEventListener('change', applyFormat);
    element.addEventListener('paste', () => setTimeout(applyFormat, 0));
    element.addEventListener('input', handleInput);
    element.addEventListener('keydown', handleBackspace);
    element.addEventListener('keydown', handleEnter);
};

bindAutoformat(ingredients, formatIngredients);
bindAutoformat(steps, formatInstructions);
