package retrywindow

import (
	"fmt"
	"strings"
	"time"
)

const (
	Min = time.Second
	Max = 5 * time.Minute
)

// Parse converts an operator-provided retry window into a duration.
func Parse(input string) (time.Duration, error) {
	duration, err := time.ParseDuration(strings.TrimSpace(input))
	if err != nil {
		return 0, fmt.Errorf("parse retry window: %w", err)
	}
	if duration < Min || duration > Max {
		return 0, fmt.Errorf("retry window must be between %s and %s", Min, Max)
	}

	return duration, nil
}
