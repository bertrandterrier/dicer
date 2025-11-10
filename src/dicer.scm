; --- Define Globals ---
(define lexer '())
(define buf '())
(define curr-char "SOF")
(define tree '())
(define inner-elem '())

(define (tokenize! src pos)
  (let ((i (if (null? pos) (string-length src) pos))
	(char (string-ref src pos)))
    (if (not (eqv? char #\space))
      (begin (set! lexer (cons char lexer))
	     (set! pos (- pos 1)))
      (begin (set! pos (- pos 1))
	     (if ((not (eqv? #\; (car lexer)))
		  (set ! lexer (cons #\; lexer)))))))
  (tokenize! src pos))

(define (walk!)
  (cond ((string? buf) (set! curr-char buf))
	((list? buf) (begin
		       (set! curr-char (cdr buf))
		       (if ((list? (car buf)) (set! buf (append (car buf)) '()))
					      (set! buf (car buf)))))
	(else (set! curr-char "EOF"))))


(define (group?) #f)


(define (parse!)
  (cond ((eqv? char #\() (if ((not (group?)) (error "Unexpected behaviour. Group was only option")
					     (begin (walk!) (parse!)))))
	((eqv? char #\d) (if ((not (dice?)) (error "Unexpected behaviour.\n\"d\" is always triggering DICE")
					    (begin (walk!) (parse!)))))
	((eqv? char #\[) (error "Scalar constructor cannot stand alone.\nNeeds 'dice[<<scalar>>]' or insode of function."))
	((eqv? char (#\)#\}#\]) (error "Cannot close here.\nSuspect missing openeing.")))
	((eqv? char #\;) (begin (display "Unexpected ';'")
				(walk!)
				(parse!))))

(define (init-parse!)
  (set! buf (append (cdr lexer) '()))
  (let ((curr-char (car lexer))))
  (parse!))
