package chapter02;

/**
 * Minimal example of keeping business code independent of a concrete model provider.
 * Production implementations should add timeouts, telemetry, validation and error mapping.
 */
public final class ModelBoundaryExample {

    public interface AiTextGenerator {
        AiResponse generate(AiRequest request);
    }

    public record AiRequest(
            String systemInstruction,
            String userInput,
            String model,
            double temperature) {
    }

    public record AiResponse(
            String text,
            String model,
            int inputTokens,
            int outputTokens) {
    }

    public static final class CustomerSupportService {
        private final AiTextGenerator generator;

        public CustomerSupportService(AiTextGenerator generator) {
            this.generator = generator;
        }

        public String draftReply(String customerMessage) {
            var request = new AiRequest(
                    "Answer using only approved support guidance.",
                    customerMessage,
                    "configured-by-platform",
                    0.2);

            return generator.generate(request).text();
        }
    }
}
