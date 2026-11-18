; Dominio del rover de la nota 2b (STRIPS con tipos).
; Se puede probar con: pyperplan -s astar -H hmax rover-dominio.pddl rover-problema.pddl
(define (domain rover)
  (:requirements :strips :typing)
  (:types lugar muestra)
  (:predicates (en ?x - lugar)
               (conectado ?x ?y - lugar)
               (muestra-en ?m - muestra ?x - lugar)
               (tiene ?m - muestra)
               (analizada ?m - muestra)
               (transmitida ?m - muestra)
               (zona-com ?x - lugar))

  (:action mover
    :parameters (?desde ?hasta - lugar)
    :precondition (and (en ?desde) (conectado ?desde ?hasta))
    :effect (and (en ?hasta) (not (en ?desde))))

  (:action tomar
    :parameters (?m - muestra ?x - lugar)
    :precondition (and (en ?x) (muestra-en ?m ?x))
    :effect (and (tiene ?m) (not (muestra-en ?m ?x))))

  (:action analizar
    :parameters (?m - muestra)
    :precondition (tiene ?m)
    :effect (analizada ?m))

  (:action transmitir
    :parameters (?m - muestra ?x - lugar)
    :precondition (and (analizada ?m) (en ?x) (zona-com ?x))
    :effect (transmitida ?m)))
