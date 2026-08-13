package retrywindow

import (
	"testing"
	"time"
)

func TestParseAcceptsTrimmedDuration(t *testing.T) {
	duration, err := Parse(" 30s ")
	if err != nil {
		t.Fatalf("Parse() returned error: %v", err)
	}

	if duration != 30*time.Second {
		t.Fatalf("Parse() = %v, want %v", duration, 30*time.Second)
	}
}

func TestParseAcceptsInclusiveBounds(t *testing.T) {
	tests := []struct {
		name  string
		input string
		want  time.Duration
	}{
		{name: "minimum", input: "1s", want: time.Second},
		{name: "maximum", input: "5m", want: 5 * time.Minute},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			duration, err := Parse(test.input)
			if err != nil {
				t.Fatalf("Parse(%q) returned error: %v", test.input, err)
			}
			if duration != test.want {
				t.Fatalf("Parse(%q) = %v, want %v", test.input, duration, test.want)
			}
		})
	}
}

func TestParseEnforcesRetryWindowRange(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{name: "below minimum", input: "999ms"},
		{name: "above maximum", input: "5m1s"},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if _, err := Parse(test.input); err == nil {
				t.Fatalf("Parse(%q) returned no error", test.input)
			}
		})
	}
}

func TestParseRejectsInvalidDuration(t *testing.T) {
	if _, err := Parse("not-a-duration"); err == nil {
		t.Fatal("Parse() returned no error for invalid duration syntax")
	}
}

func FuzzParseNeverAcceptsOutOfRangeDuration(f *testing.F) {
	for _, seed := range []string{"1s", "30s", "5m", "999ms", "5m1s", "", " 30s "} {
		f.Add(seed)
	}

	f.Fuzz(func(t *testing.T, input string) {
		duration, err := Parse(input)
		if err == nil && (duration < Min || duration > Max) {
			t.Fatalf("Parse(%q) accepted out-of-range duration %v", input, duration)
		}
	})
}
