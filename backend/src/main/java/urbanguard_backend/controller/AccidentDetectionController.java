package urbanguard_backend.controller;

import urbanguard_backend.model.AccidentDetection;
import urbanguard_backend.service.AccidentDetectionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/accidents")
@CrossOrigin(origins = "*")
public class AccidentDetectionController {

    private final AccidentDetectionService accidentDetectionService;

    public AccidentDetectionController(
            AccidentDetectionService accidentDetectionService) {
        this.accidentDetectionService = accidentDetectionService;
    }

    // Create accident detection
    @PostMapping
    public ResponseEntity<AccidentDetection> createDetection(
            @RequestBody AccidentDetection detection) {

        return ResponseEntity.ok(
                accidentDetectionService.saveDetection(detection)
        );
    }

    // Get all accident detections
    @GetMapping
    public ResponseEntity<List<AccidentDetection>> getAllDetections() {
        return ResponseEntity.ok(
                accidentDetectionService.getAllDetections()
        );
    }

    // Get accident detection by ID
    @GetMapping("/{id}")
    public ResponseEntity<AccidentDetection> getDetectionById(
            @PathVariable Long id) {

        return ResponseEntity.ok(
                accidentDetectionService.getDetectionById(id)
        );
    }

    // Delete accident detection
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDetection(
            @PathVariable Long id) {

        accidentDetectionService.deleteDetection(id);
        return ResponseEntity.noContent().build();
    }
}